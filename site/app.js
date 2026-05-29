const galleryTarget = document.querySelector("#gallery-list");

function text(value) {
  return typeof value === "string" ? value : "";
}

function element(tag, className, value) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (value !== undefined) {
    node.textContent = text(value);
  }
  return node;
}

function field(label, value, className) {
  const paragraph = element("p", className);
  const strong = element("strong", "", `${label}:`);
  paragraph.append(strong, " ", text(value));
  return paragraph;
}

function card(example) {
  const article = document.createElement("article");
  article.className = "gallery-card";

  const header = document.createElement("header");
  const titleBlock = document.createElement("div");
  titleBlock.append(element("p", "case-id", example.eval_case), element("h3", "", example.title));
  header.append(titleBlock, element("span", "case-id", example.id));

  const compare = element("div", "compare");
  const weak = element("div", "weak");
  weak.append(element("h3", "", "Weak pattern"), element("p", "", example.weak_pattern));
  const strong = element("div", "strong");
  strong.append(element("h3", "", "Converge pattern"), element("p", "", example.converge_pattern));
  compare.append(weak, strong);

  article.append(
    header,
    field("User input", example.user_input),
    compare,
    field("Why better", example.why_better),
    field("Proof boundary", example.proof_boundary, "proof")
  );
  return article;
}

async function loadGallery() {
  if (!galleryTarget) {
    return;
  }
  try {
    const response = await fetch("../gallery/examples.json");
    if (!response.ok) {
      throw new Error(`Gallery request failed: ${response.status}`);
    }
    const data = await response.json();
    const examples = Array.isArray(data.examples) ? data.examples : [];
    galleryTarget.replaceChildren(...examples.map(card));
  } catch (error) {
    const article = element("article", "gallery-card");
    article.append(
      element("h3", "", "Gallery data unavailable"),
      element("p", "", "Open this site through a local or hosted web server so the browser can load gallery/examples.json.")
    );
    galleryTarget.replaceChildren(article);
  }
}

loadGallery();
