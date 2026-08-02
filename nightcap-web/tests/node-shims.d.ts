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
    doesNotThrow(fn: () => unknown, message?: string): void;
  };

  export default assert;
}

declare module "node:vm" {
  const vm: {
    runInNewContext(code: string, sandbox?: object): unknown;
  };
  export default vm;
}
