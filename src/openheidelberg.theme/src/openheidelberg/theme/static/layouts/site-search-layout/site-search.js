/* Start page search: shows the clear button (x) while the field has text. Enter submits the form natively. */
document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('searchableText');
  var clearBtn = document.getElementById('clear-search');
  if (!searchInput || !clearBtn) {
    return;
  }
  searchInput.addEventListener('input', function () {
    clearBtn.style.display = this.value.length > 0 ? 'block' : 'none';
  });
  clearBtn.addEventListener('click', function () {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    searchInput.focus();
  });
});
