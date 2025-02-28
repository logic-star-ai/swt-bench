// making specific table sortable
function makeSortable(table) {
  const headers = table.querySelectorAll("th");

  tbody = table.querySelector("tbody");
  function sortByIndex(index) {
      sortTableByColumn(tbody, index);
      updateArrows(headers, index);
 };
  headers.forEach((header, index) => {
    header.addEventListener("click", () => sortByIndex(index));
  });

  function sortTableByColumn(table, columnIndex) {
    const rows = Array.from(table.querySelectorAll("tr"));
    const isAscending = table.getAttribute("data-sort-asc") !== "false";
    const direction = isAscending ? -1 : 1;

    rows.sort((rowA, rowB) => {
      const cellA = rowA.children[columnIndex].textContent.trim();
      const cellB = rowB.children[columnIndex].textContent.trim();

      const cellANum = parseFloat(cellA);
      const cellBNum = parseFloat(cellB);

      if (!isNaN(cellANum) && !isNaN(cellBNum)) {
        return direction * (cellANum - cellBNum);
      } else {
        return direction * cellA.localeCompare(cellB);
      }
    });

    rows.forEach(row => table.appendChild(row));
    table.setAttribute("data-sort-asc", !isAscending);
  }

  function updateArrows(headers, sortedColumnIndex) {
    headers.forEach((header, index) => {
      const arrow = header.querySelector(".sort-arrow");
      arrow.setAttribute("act-column", index == sortedColumnIndex);
      if (!arrow) {
        return;
      }
      if (index === sortedColumnIndex) {
        const isAscending = tbody.getAttribute("data-sort-asc") === "true";
        arrow.textContent = isAscending ? "\xa0\xa0🔼" : "\xa0\xa0🔽";
      } else {

        arrow.textContent = "️\xa0\xa0\xa0";
      }
    });
  }
  sortByIndex(1);
}
document.addEventListener("DOMContentLoaded", () => {
  makeSortable(document.getElementById("leaderboard-table"));
});

function selectElement(element) {
  const range = document.createRange();
  range.selectNodeContents(element);
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('table time').forEach(function(cell) {
    const fullDate = cell.textContent;
    const parsedDate = new Date(fullDate);
    // display only month/year
    const shortDate = parsedDate.toLocaleDateString('en-US', { month: 'short'}) + ' \'' + (parsedDate.getFullYear()%100);
    const longDate = parsedDate.toLocaleDateString();
    cell.setAttribute('data-short-date', shortDate);
    cell.setAttribute('data-long-date', longDate);
    cell.textContent = "";
    cell.setAttribute('title', longDate);
  });
});
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('strong time').forEach(function(cell) {
    const fullDate = cell.textContent;
    const parsedDate = new Date(fullDate);
    // display only month/year
    const shortDate = parsedDate.toLocaleDateString('en-US', { month: 'short'}) + ' \'' + (parsedDate.getFullYear()%100);
    const longDate = parsedDate.toLocaleDateString();
    cell.textContent = longDate;
  });
  document.getElementById('lite-button').addEventListener('click', function() {
    document.getElementById('leaderboard-table').parentElement.style.display = 'block';
    document.getElementById('verified-leaderboard').style.display = 'none';
    document.getElementById('lite-button').classList.add('is-link');
    document.getElementById('verified-button').classList.remove('is-link');
    urlParams.set('results', 'lite');
    window.history.replaceState({}, '', `${location.pathname}?${urlParams}`);
  });

  document.getElementById('verified-button').addEventListener('click', function() {
    document.getElementById('leaderboard-table').parentElement.style.display = 'none';
    document.getElementById('verified-leaderboard').style.display = 'block';
    document.getElementById('lite-button').classList.remove('is-link');
    document.getElementById('verified-button').classList.add('is-link');
    urlParams.set('results', 'verified');
    window.history.replaceState({}, '', `${location.pathname}?${urlParams}`);
  });
  const urlParams = new URLSearchParams(window.location.search);
  const resultsParam = urlParams.get('results');

  if (resultsParam === 'verified') {
    document.getElementById('verified-button').click();
  } else if (resultsParam === 'lite') {
    document.getElementById('lite-button').click();
  }
});