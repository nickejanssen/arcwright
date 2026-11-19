// import.meta.glob is a Vite feature. The dashboard's vite-env.d.ts does not
// load vite/client types, so the two forms registry-bindings.ts uses are
// declared here.
interface ImportMeta {
  glob<T = unknown>(
    pattern: string | string[],
    options: { eager: true; import?: string },
  ): Record<string, T>;
  glob<T = unknown>(
    pattern: string | string[],
    options?: { eager?: false; import?: string },
  ): Record<string, () => Promise<T>>;
}
