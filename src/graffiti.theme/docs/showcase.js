/* Behaviour of the static page docs/showcase.html: the clear button of the search field. */
document.addEventListener('DOMContentLoaded', function () {
  var searchForm = document.getElementById('search');
  var searchInput = document.getElementById('searchableText');
  var clearBtn = document.getElementById('clear-search');

  if (searchInput && clearBtn) {
    searchInput.addEventListener('input', function () {
      clearBtn.style.display = this.value.length > 0 ? 'block' : 'none';
    });

    clearBtn.addEventListener('click', function () {
      searchInput.value = '';
      clearBtn.style.display = 'none';
      searchInput.focus();
    });

    searchInput.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        searchForm.submit();
      }
    });
  }
});
