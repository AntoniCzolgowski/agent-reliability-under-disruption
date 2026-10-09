// Shared site constants. Tab names are fixed by the assignment and must not change (list revised 9 Oct 2026: SVMs and NN replaced by AdaBoost, GradientBoosting, XGBoost).
export const SITE_TITLE = "Agent reliability under disruption";
export const AUTHOR = "Antoni Czolgowski";
export const REPO_URL = "https://github.com/AntoniCzolgowski/agent-reliability-under-disruption";

export const COURSE_TABS = [
  { label: "Introduction", slug: "introduction" },
  { label: "DataPrep_EDA", slug: "dataprep_eda" },
  { label: "Clustering", slug: "clustering" },
  { label: "PCA", slug: "pca" },
  { label: "NaiveBayes", slug: "naivebayes" },
  { label: "DecTrees", slug: "dectrees" },
  { label: "Regression", slug: "regression" },
  { label: "AdaBoost", slug: "adaboost" },
  { label: "GradientBoosting", slug: "gradientboosting" },
  { label: "XGBoost", slug: "xgboost" },
  { label: "Conclusions", slug: "conclusions" },
];

export const EXTRA_TABS = [
  { label: "Research", slug: "research" },
  { label: "About Me", slug: "about" },
];

// Prefix a site path with the base path. Accepts "introduction/" or "/introduction/".
export function url(path = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${base}/${path.replace(/^\//, "")}`;
}
