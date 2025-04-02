// making specific table sortable
function makeSortable(table) {

  const headers = table.querySelectorAll("th");
  const tbody = table.querySelector("tbody");
  tbody.setAttribute("data-sort-asc", false);
  tbody.setAttribute("data-sort-index", -1);

  function sortTableByColumn(table, columnIndex) {
    const rows = Array.from(table.querySelectorAll("tr"));
    let isAscending = table.getAttribute("data-sort-asc") !== "false";
    const sortedIndex = parseInt(table.getAttribute("data-sort-index"));
    if(sortedIndex === columnIndex) {
      // Flip the sort direction if we're sorting the same column
      isAscending = !isAscending;
    }
    table.setAttribute("data-sort-index", columnIndex);
    const direction = isAscending ? 1 : -1;
    table.setAttribute("data-sort-asc", isAscending.toString());

    rows.sort((rowA, rowB) => {
      let cellA = rowA.children[columnIndex].textContent.trim();
      let cellB = rowB.children[columnIndex].textContent.trim();
      if (!cellA && !cellB) {
        // check if its a date
        cellA = new Date(rowA.children[columnIndex].querySelector('time').getAttribute('data-long-date')).getTime();
        cellB = new Date(rowB.children[columnIndex].querySelector('time').getAttribute('data-long-date')).getTime();
      }

      const cellANum = parseFloat(cellA);
      const cellBNum = parseFloat(cellB);

      if (!isNaN(cellANum) && !isNaN(cellBNum)) {
        return direction * (cellANum - cellBNum);
      } else {
        return direction * cellA.localeCompare(cellB);
      }
    });

    rows.forEach(row => table.appendChild(row));
  }

  function updateArrows(headers, sortedColumnIndex) {
    headers.forEach((header, index) => {
      const arrow = header.querySelector(".sort-arrow");
      if (!arrow) {
        return;
      }
      arrow.setAttribute("act-column", index == sortedColumnIndex);
      if (index === sortedColumnIndex) {
        const isAscending = tbody.getAttribute("data-sort-asc") !== "false";
        arrow.textContent = isAscending ? "\xa0\xa0⬆️" : "\xa0\xa0⬇️";
      } else {

        arrow.textContent = "️\xa0\xa0\xa0";
      }
    });
  }

  function sortByIndex(index) {
      sortTableByColumn(tbody, index);
      updateArrows(headers, index);
  };
  headers.forEach((header, index) => {
    header.addEventListener("click", () => sortByIndex(index));
  });

  sortByIndex(2);
}
document.addEventListener("DOMContentLoaded", () => {
  makeSortable(document.getElementById("leaderboard-table"));
  makeSortable(document.getElementById("verified-leaderboard-table"));
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
document.addEventListener('DOMContentLoaded', function () {
  const reproductionCheckbox = document.getElementById('reproduction-mode-checkbox');
  const nonReproductionCheckbox = document.getElementById('unittest-mode-checkbox');
  const rows = document.querySelectorAll('#leaderboard-table tbody tr');

  function updateRowVisibility() {
    rows.forEach(row => {
      const mode = row.getAttribute('data-mode');
      if (
        (mode === 'reproduction' && !reproductionCheckbox.checked) ||
        (mode === 'unittest' && !nonReproductionCheckbox.checked)
      ) {
        row.style.backgroundColor = '#f0f0f0';
      } else {
        row.style.backgroundColor = '';
      }
    });
  }

  reproductionCheckbox.addEventListener('change', updateRowVisibility);
  nonReproductionCheckbox.addEventListener('change', updateRowVisibility);

  updateRowVisibility(); // Initialize visibility
});