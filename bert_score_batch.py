import os
import pathlib
import sys
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import tqdm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from transformers import AutoTokenizer

from bert_score.utils import (bert_cos_score_idf, cache_scibert, get_bert_embedding,
                    get_hash, get_idf_dict, get_model, get_tokenizer,
                    lang2model, model2layers, sent_encode,
                    pad_sequence, greedy_cos_idf)

__all__ = ["score", "plot_example"]

def bert_cos_score_idf(
    model,
    refs,
    hyps,
    tokenizer,
    idf_dict,
    verbose=False,
    batch_size=64,
    device="cuda:0",
    all_layers=False,
):
    """
    Compute BERTScore.

    Args:
        - :param: `model` : a BERT model in `pytorch_pretrained_bert`
        - :param: `refs` (list of str): reference sentences
        - :param: `hyps` (list of str): candidate sentences
        - :param: `tokenzier` : a BERT tokenizer corresponds to `model`
        - :param: `idf_dict` : a dictionary mapping a word piece index to its
                               inverse document frequency
        - :param: `verbose` (bool): turn on intermediate status update
        - :param: `batch_size` (int): bert score processing batch size
        - :param: `device` (str): device to use, e.g. 'cpu' or 'cuda'
    """
    preds = []

    def dedup_and_sort(l):
        return sorted(list(set(l)), key=lambda x: len(x.split(" ")), reverse=True)

    sentences = dedup_and_sort(refs + hyps)
    embs = []
    iter_range = range(0, len(sentences), batch_size)
    if verbose:
        print("computing bert embedding.")
        print(type(iter_range))
        iter_range = tqdm(iter_range)
    stats_dict = dict()
    for batch_start in iter_range:
        sen_batch = sentences[batch_start : batch_start + batch_size]
        embs, masks, padded_idf = get_bert_embedding(
            sen_batch, model, tokenizer, idf_dict, device=device, all_layers=all_layers
        )
        embs = embs.cpu()
        masks = masks.cpu()
        padded_idf = padded_idf.cpu()
        for i, sen in enumerate(sen_batch):
            sequence_len = masks[i].sum().item()
            emb = embs[i, :sequence_len]
            idf = padded_idf[i, :sequence_len]
            stats_dict[sen] = (emb, idf)

    def pad_batch_stats(sen_batch, stats_dict, device):
        stats = [stats_dict[s] for s in sen_batch]
        emb, idf = zip(*stats)
        emb = [e.to(device) for e in emb]
        idf = [i.to(device) for i in idf]
        lens = [e.size(0) for e in emb]
        emb_pad = pad_sequence(emb, batch_first=True, padding_value=2.0)
        idf_pad = pad_sequence(idf, batch_first=True)

        def length_to_mask(lens):
            lens = torch.tensor(lens, dtype=torch.long)
            max_len = max(lens)
            base = torch.arange(max_len, dtype=torch.long).expand(len(lens), max_len)
            return base < lens.unsqueeze(1)

        pad_mask = length_to_mask(lens).to(device)
        return emb_pad, pad_mask, idf_pad

    device = next(model.parameters()).device
    iter_range = range(0, len(refs), batch_size)
    if verbose:
        print("computing greedy matching.")
        iter_range = tqdm(iter_range)

    with torch.no_grad():
        for batch_start in iter_range:
            batch_refs = refs[batch_start : batch_start + batch_size]
            batch_hyps = hyps[batch_start : batch_start + batch_size]
            ref_stats = pad_batch_stats(batch_refs, stats_dict, device)
            hyp_stats = pad_batch_stats(batch_hyps, stats_dict, device)

            P, R, F1 = greedy_cos_idf(*ref_stats, *hyp_stats, all_layers)
            preds.append(torch.stack((P, R, F1), dim=-1).cpu())
    preds = torch.cat(preds, dim=1 if all_layers else 0)
    return preds

def batch_score(
    cands,
    refs,
    model_type=None,
    num_layers=None,
    verbose=False,
    idf=False,
    device=None,
    batch_size=64,
    nthreads=4,
    all_layers=False,
    lang=None,
    return_hash=False,
    rescale_with_baseline=False,
    baseline_path=None,
    use_fast_tokenizer=False,
    tokenizer_input=None,
    model_input=None,
):
    """
    BERTScore metric.

    Args:
        - :param: `cands` (list of str): candidate sentences
        - :param: `refs` (list of str or list of list of str): reference sentences
        - :param: `model_type` (str): bert specification, default using the suggested
                  model for the target langauge; has to specify at least one of
                  `model_type` or `lang`
        - :param: `num_layers` (int): the layer of representation to use.
                  default using the number of layer tuned on WMT16 correlation data
        - :param: `verbose` (bool): turn on intermediate status update
        - :param: `idf` (bool or dict): use idf weighting, can also be a precomputed idf_dict
        - :param: `device` (str): on which the contextual embedding model will be allocated on.
                  If this argument is None, the model lives on cuda:0 if cuda is available.
        - :param: `nthreads` (int): number of threads
        - :param: `batch_size` (int): bert score processing batch size
        - :param: `lang` (str): language of the sentences; has to specify
                  at least one of `model_type` or `lang`. `lang` needs to be
                  specified when `rescale_with_baseline` is True.
        - :param: `return_hash` (bool): return hash code of the setting
        - :param: `rescale_with_baseline` (bool): rescale bertscore with pre-computed baseline
        - :param: `baseline_path` (str): customized baseline file
        - :param: `use_fast_tokenizer` (bool): `use_fast` parameter passed to HF tokenizer

    Return:
        - :param: `(P, R, F)`: each is of shape (N); N = number of input
                  candidate reference pairs. if returning hashcode, the
                  output will be ((P, R, F), hashcode). If a candidate have
                  multiple references, the returned score of this candidate is
                  the *best* score among all references.
    """
    # assert len(cands) == len(refs), "Different number of candidates and references"

    assert (
        lang is not None or model_type is not None
    ), "Either lang or model_type should be specified"

    ref_group_boundaries = None
    if not isinstance(refs[0], str):
        ref_group_boundaries = []
        ori_cands, ori_refs = cands, refs
        cands, refs = [], []
        count = 0
        for cand, ref_group in zip(ori_cands, ori_refs):
            cands += [cand] * len(ref_group)
            refs += ref_group
            ref_group_boundaries.append((count, count + len(ref_group)))
            count += len(ref_group)

    if rescale_with_baseline:
        assert lang is not None, "Need to specify Language when rescaling with baseline"

    if model_type is None:
        lang = lang.lower()
        model_type = lang2model[lang]
    if num_layers is None:
        num_layers = model2layers[model_type]

    tokenizer = tokenizer_input
    model = model_input
    # tokenizer = get_tokenizer(model_type, use_fast_tokenizer)
    # model = get_model(model_type, num_layers, all_layers)
    # if device is None:
    #     device = "cuda" if torch.cuda.is_available() else "cpu"
    # model.to(device)

    if not idf:
        idf_dict = defaultdict(lambda: 1.0)
        # set idf for [SEP] and [CLS] to 0
        idf_dict[tokenizer.sep_token_id] = 0
        idf_dict[tokenizer.cls_token_id] = 0
    elif isinstance(idf, dict):
        if verbose:
            print("using predefined IDF dict...")
        idf_dict = idf
    else:
        if verbose:
            print("preparing IDF dict...")
        start = time.perf_counter()
        idf_dict = get_idf_dict(refs, tokenizer, nthreads=nthreads)
        if verbose:
            print("done in {:.2f} seconds".format(time.perf_counter() - start))

    if verbose:
        print("calculating scores...")
    start = time.perf_counter()
    all_preds = bert_cos_score_idf(
        model,
        refs,
        cands,
        tokenizer,
        idf_dict,
        verbose=verbose,
        device=device,
        batch_size=batch_size,
        all_layers=all_layers,
    ).cpu()

    if ref_group_boundaries is not None:
        max_preds = []
        for beg, end in ref_group_boundaries:
            max_preds.append(all_preds[beg:end].max(dim=0)[0])
        all_preds = torch.stack(max_preds, dim=0)

    use_custom_baseline = baseline_path is not None
    if rescale_with_baseline:
        if baseline_path is None:
            baseline_path = os.path.join(
                os.path.dirname(__file__), f"rescale_baseline/{lang}/{model_type}.tsv"
            )
        if os.path.isfile(baseline_path):
            if not all_layers:
                baselines = torch.from_numpy(
                    pd.read_csv(baseline_path).iloc[num_layers].to_numpy()
                )[1:].float()
            else:
                baselines = (
                    torch.from_numpy(pd.read_csv(baseline_path).to_numpy())[:, 1:]
                    .unsqueeze(1)
                    .float()
                )

            all_preds = (all_preds - baselines) / (1 - baselines)
        else:
            print(
                f"Warning: Baseline not Found for {model_type} on {lang} at {baseline_path}",
                file=sys.stderr,
            )

    out = all_preds[..., 0], all_preds[..., 1], all_preds[..., 2]  # P, R, F

    if verbose:
        time_diff = time.perf_counter() - start
        print(
            f"done in {time_diff:.2f} seconds, {len(refs) / time_diff:.2f} sentences/sec"
        )

    if return_hash:
        return tuple(
            [
                out,
                get_hash(
                    model_type,
                    num_layers,
                    idf,
                    rescale_with_baseline,
                    use_custom_baseline=use_custom_baseline,
                    use_fast_tokenizer=use_fast_tokenizer,
                ),
            ]
        )

    return out
