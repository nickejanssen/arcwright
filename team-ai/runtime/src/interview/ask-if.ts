// Deterministic. No model calls. No network. No `eval`, no `new Function`.
//
// `ask_if` is the gate expression on every interview question. Both runtimes
// (the CLI prompts and the in-Claude skill) evaluate it through this one
// function so a question is shown, or hidden, identically everywhere.
//
// Grammar (see the header of `questions.yaml`):
//   always
//   <id> == "value"
//   <id> != "value"
//   <id> in ["a", "b", ...]
//   has(<id>, "value")
//   ( <expr> )
//   <expr> && <expr>          -- binds tighter than ||
//   <expr> || <expr>
//
// An unknown identifier resolves to `undefined` and never throws: `== ` is
// false, `!=` is true, `in` / `has` are false. A malformed expression is an
// authoring bug and throws at parse time.

type Node =
  | { t: "always" }
  | { t: "eq"; id: string; val: string }
  | { t: "neq"; id: string; val: string }
  | { t: "in"; id: string; list: string[] }
  | { t: "has"; id: string; val: string }
  | { t: "and"; l: Node; r: Node }
  | { t: "or"; l: Node; r: Node };

type TokKind = "word" | "str" | "eq" | "neq" | "and" | "or" | "(" | ")" | "[" | "]" | ",";

interface Token {
  k: TokKind;
  v?: string;
}

function parseError(expr: string, detail: string): Error {
  return new Error(`ask_if parse error in '${expr}': ${detail}`);
}

function tokenize(expr: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  while (i < expr.length) {
    const c = expr[i] as string;
    if (c === " " || c === "\t" || c === "\n" || c === "\r") {
      i++;
      continue;
    }
    if (c === '"') {
      let j = i + 1;
      while (j < expr.length && expr[j] !== '"') j++;
      if (j >= expr.length) throw parseError(expr, `unterminated string starting at ${i}`);
      out.push({ k: "str", v: expr.slice(i + 1, j) });
      i = j + 1;
      continue;
    }
    const two = expr.slice(i, i + 2);
    if (two === "==") {
      out.push({ k: "eq" });
      i += 2;
      continue;
    }
    if (two === "!=") {
      out.push({ k: "neq" });
      i += 2;
      continue;
    }
    if (two === "&&") {
      out.push({ k: "and" });
      i += 2;
      continue;
    }
    if (two === "||") {
      out.push({ k: "or" });
      i += 2;
      continue;
    }
    if (c === "(" || c === ")" || c === "[" || c === "]" || c === ",") {
      out.push({ k: c });
      i++;
      continue;
    }
    if (/[A-Za-z_]/.test(c)) {
      let j = i;
      while (j < expr.length && /[A-Za-z0-9_.]/.test(expr[j] as string)) j++;
      out.push({ k: "word", v: expr.slice(i, j) });
      i = j;
      continue;
    }
    throw parseError(expr, `unexpected character '${c}' at position ${i}`);
  }
  return out;
}

class Parser {
  private p = 0;

  constructor(
    private readonly expr: string,
    private readonly tokens: Token[],
  ) {}

  parse(): Node {
    if (this.tokens.length === 0) throw parseError(this.expr, "empty expression");
    const node = this.parseOr();
    if (this.p < this.tokens.length) {
      throw parseError(this.expr, `unexpected trailing token near position ${this.p}`);
    }
    return node;
  }

  private peek(): Token | undefined {
    return this.tokens[this.p];
  }

  private nextTok(): Token {
    const t = this.tokens[this.p];
    if (!t) throw parseError(this.expr, "unexpected end of expression");
    this.p++;
    return t;
  }

  private expect(k: TokKind): Token {
    const t = this.nextTok();
    if (t.k !== k) throw parseError(this.expr, `expected '${k}' but found '${t.k}'`);
    return t;
  }

  private expectStr(): string {
    return this.expect("str").v ?? "";
  }

  private parseOr(): Node {
    let left = this.parseAnd();
    while (this.peek()?.k === "or") {
      this.p++;
      left = { t: "or", l: left, r: this.parseAnd() };
    }
    return left;
  }

  private parseAnd(): Node {
    let left = this.parsePrimary();
    while (this.peek()?.k === "and") {
      this.p++;
      left = { t: "and", l: left, r: this.parsePrimary() };
    }
    return left;
  }

  private parsePrimary(): Node {
    const t = this.nextTok();
    if (t.k === "(") {
      const inner = this.parseOr();
      this.expect(")");
      return inner;
    }
    if (t.k === "word") {
      const w = t.v ?? "";
      if (w === "always") return { t: "always" };
      if (w === "has") {
        this.expect("(");
        const idTok = this.expect("word");
        this.expect(",");
        const val = this.expectStr();
        this.expect(")");
        return { t: "has", id: idTok.v ?? "", val };
      }
      const op = this.nextTok();
      if (op.k === "eq") return { t: "eq", id: w, val: this.expectStr() };
      if (op.k === "neq") return { t: "neq", id: w, val: this.expectStr() };
      if (op.k === "word" && op.v === "in") {
        this.expect("[");
        const list: string[] = [this.expectStr()];
        while (this.peek()?.k === ",") {
          this.p++;
          list.push(this.expectStr());
        }
        this.expect("]");
        return { t: "in", id: w, list };
      }
      throw parseError(this.expr, `expected '==', '!=' or 'in' after '${w}'`);
    }
    throw parseError(this.expr, `unexpected token '${t.k}'`);
  }
}

function matchScalar(v: unknown, s: string): boolean {
  if (v === undefined || v === null) return false;
  if (typeof v === "string") return v === s;
  if (typeof v === "number" || typeof v === "boolean") return String(v) === s;
  return false;
}

function evalNode(node: Node, answers: Record<string, unknown>): boolean {
  switch (node.t) {
    case "always":
      return true;
    case "and":
      return evalNode(node.l, answers) && evalNode(node.r, answers);
    case "or":
      return evalNode(node.l, answers) || evalNode(node.r, answers);
    case "eq":
      return matchScalar(answers[node.id], node.val);
    case "neq":
      return !matchScalar(answers[node.id], node.val);
    case "in": {
      const v = answers[node.id];
      if (Array.isArray(v)) return v.some((e) => node.list.some((item) => matchScalar(e, item)));
      return node.list.some((item) => matchScalar(v, item));
    }
    case "has": {
      const v = answers[node.id];
      if (Array.isArray(v)) return v.includes(node.val);
      return v === node.val;
    }
    default: {
      const never: never = node;
      return never;
    }
  }
}

export function evalAskIf(expr: string, answers: Record<string, unknown>): boolean {
  const ast = new Parser(expr, tokenize(expr)).parse();
  return evalNode(ast, answers);
}
