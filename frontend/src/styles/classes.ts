export const layout = {
  page: "min-h-screen bg-stone-100 px-4 py-6 sm:px-6 lg:px-8 flex items-center justify-center text-stone-900",
  card: "w-full max-w-3xl rounded-[2rem] border border-stone-200 bg-white/90 p-6 shadow-2xl shadow-stone-300/40 sm:p-10",
  chatPage:
    "grid min-h-screen grid-rows-[auto_1fr_auto] bg-stone-100 text-stone-900",
};

export const text = {
  h1: "my-4 text-5xl font-bold tracking-tight text-stone-900 sm:text-6xl lg:text-7xl",
  h2: "my-4 text-4xl font-bold tracking-tight text-stone-900 sm:text-5xl",
  hero: "max-w-2xl text-lg leading-8 text-stone-700 sm:text-xl",
  muted: "text-base leading-7 text-stone-600 sm:text-lg",
};

export const buttons = {
  primary:
    "rounded-2xl bg-green-800 px-6 py-4 text-base font-bold text-white transition hover:-translate-y-0.5 hover:bg-green-900 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0",
  secondary:
    "rounded-2xl bg-stone-200 px-5 py-3 text-sm font-bold text-stone-800 transition hover:-translate-y-0.5 hover:bg-stone-300",
  text: "mb-5 text-left font-bold text-green-800 transition hover:text-green-950",
};

export const forms = {
  label: "my-5 grid gap-2 font-bold text-stone-800",
  input:
    "w-full rounded-2xl border border-stone-300 bg-white px-4 py-3 text-stone-900 outline-none transition focus:border-green-800 focus:ring-4 focus:ring-green-800/10",
  checkboxLabel: "my-6 flex items-start gap-3 text-stone-700",
  checkbox: "mt-1 h-5 w-5 rounded border-stone-300",
};

export const badges = {
  default:
    "inline-flex w-fit rounded-full bg-amber-100 px-4 py-2 text-sm font-bold text-amber-900",
  demo: "inline-flex w-fit rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-900",
  backend:
    "inline-flex w-fit rounded-full bg-green-100 px-4 py-2 text-sm font-bold text-green-900",
};

export const notices = {
  safety:
    "my-7 rounded-2xl border border-amber-200 bg-amber-50 p-4 leading-7 text-stone-700",
};
