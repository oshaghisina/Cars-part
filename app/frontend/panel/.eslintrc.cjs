module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2022: true,
  },
  extends: [
    "eslint:recommended",
    "@vue/eslint-config-prettier",
    "plugin:storybook/recommended",
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  plugins: ["vue"],
  rules: {
    // Vue.js specific rules
    "vue/multi-word-component-names": "off",
    "vue/no-reserved-component-names": "off",
    "vue/require-explicit-emits": "warn",

    // General JavaScript rules
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-unused-vars": [
      "warn",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
        ignoreRestSiblings: true,
      },
    ],
    "no-undef": "error",

    // Code style - make these warnings instead of errors
    "prefer-const": "warn",
    "no-var": "warn",
    "object-shorthand": "warn",
    "prefer-template": "warn",
  },
  overrides: [
    {
      files: ["**/*.vue"],
      parser: "vue-eslint-parser",
      extends: [
        "eslint:recommended",
        "plugin:vue/vue3-recommended",
        "@vue/eslint-config-prettier",
      ],
      rules: {
        // Make Vue.js rules more lenient
        "vue/multi-word-component-names": "off",
        "vue/require-explicit-emits": "warn",
        "no-unused-vars": "warn",
        "no-undef": "error",
      },
    },
    {
      files: ["**/tests/**/*.js", "**/*.test.js", "**/*.spec.js"],
      env: {
        node: true,
        es6: true,
      },
      globals: {
        vi: "readonly",
        expect: "readonly",
        describe: "readonly",
        it: "readonly",
        test: "readonly",
        beforeEach: "readonly",
        afterEach: "readonly",
        beforeAll: "readonly",
        afterAll: "readonly",
      },
    },
  ],
};
