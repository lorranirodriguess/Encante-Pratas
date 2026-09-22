document.addEventListener("DOMContentLoaded", () => {
  const search = document.querySelector("#productSearch");
  const grid = document.querySelector("#productGrid");
  const empty = document.querySelector("#searchEmpty");

  if (!search || !grid) return;

  search.addEventListener("input", () => {
    const term = search.value.trim().toLocaleLowerCase("pt-BR");
    const cards = grid.querySelectorAll("[data-product-name]");
    const visible = Array.from(cards).reduce((count, card) => {
      const matches = card.dataset.productName.includes(term);
      card.classList.toggle("d-none", !matches);
      return count + Number(matches);
    }, 0);

    if (empty) empty.classList.toggle("d-none", visible > 0 || cards.length === 0);
  });
});
