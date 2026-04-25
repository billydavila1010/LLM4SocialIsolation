
import json
import os.path


def main():
    autobio_path = '../../autobiography_generation/guidellm/Obama/autobiography.json'
    autobio_output_dir = '../../autobiography_generation/guidellm/Obama/'
    with open(autobio_path, 'r') as f:
        autobio = json.load(f)
    for chapter_idx, chapter in enumerate(autobio):
        with open(os.path.join(autobio_output_dir, f'chapter_{chapter_idx+1}.txt'), 'w') as f:
            f.write(chapter)

if __name__ == '__main__':
    main()
