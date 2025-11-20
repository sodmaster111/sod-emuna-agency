import nextPlugin from "eslint-plugin-next";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";

const compat = new FlatCompat({
  baseDirectory: import.meta.dirname,
});

export default [
  js.configs.recommended,
  ...nextPlugin.configs.recommended,
  {
    rules: {
      "@next/next/no-html-link-for-pages": "off"
    }
  },
  ...compat.extends("plugin:react/recommended"),
];
