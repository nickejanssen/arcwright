declare module "node:test" {
  export default function test(
    name: string,
    fn: () => unknown | Promise<unknown>,
  ): void;
}

declare module "node:assert/strict" {
  const assert: {
    equal(actual: unknown, expected: unknown, message?: string): void;
    deepEqual(actual: unknown, expected: unknown, message?: string): void;
    ok(value: unknown, message?: string): void;
    match(actual: string, expected: RegExp, message?: string): void;
    doesNotMatch(actual: string, expected: RegExp, message?: string): void;
  };

  export default assert;
}

declare module "node:fs" {
  export function existsSync(path: string): boolean;
}

declare module "node:fs/promises" {
  export function mkdir(
    path: string,
    options?: { recursive?: boolean },
  ): Promise<void>;
}

declare module "node:path" {
  export function resolve(...paths: string[]): string;
}

declare module "node:url" {
  export function pathToFileURL(path: string): URL;
}
