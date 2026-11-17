import type { FrontMatter } from "../schema/types.js";

export interface KbDoc {
  id: string;
  path: string;
  frontmatter: FrontMatter;
  body: string;
  headings: string[];
  isBacklog: boolean;
}
