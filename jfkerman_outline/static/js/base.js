var isDropdownActive = false; /* Kill me */
var isTouchSupported = (('ontouchstart' in window) || (navigator.msMaxTouchPoints > 0)); /* Holy crap what the hell is this */

var onClickTransition = null;

function menu_closeDropdowns(activeBtn = null, activeDropdown = null) {
        let dropdown_buttons = document.getElementsByClassName("jfk-dropdown-btn");
        for (let i = 0; i < dropdown_buttons.length; i++) {
                if (dropdown_buttons[i] != activeBtn && dropdown_buttons[i].classList.contains('jfk-dropdown-btn-active')) {
                        dropdown_buttons[i].classList.remove('jfk-dropdown-btn-active');
                }
        }

        let dropdowns = document.getElementsByClassName("jfk-dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
                if (dropdowns[i] != activeDropdown && dropdowns[i].classList.contains('jfk-dropdown-content-show')) {
                        dropdowns[i].classList.remove('jfk-dropdown-content-show');
                }
        }
}

function menu_dropdownDelayed(activeBtn, activeDropdown) {
        if (!activeBtn.classList.contains('jfk-dropdown-btn-active') && isDropdownActive) {
                menu_closeDropdowns(activeBtn, activeDropdown);

                isDropdownActive = false;
        }
        if (activeBtn.classList.contains('jfk-dropdown-btn-active')) {
                activeDropdown.classList.remove("jfk-dropdown-content-show");
                activeBtn.classList.remove("jfk-dropdown-btn-active");

                isDropdownActive = false;
        }
        else {
                activeDropdown.classList.add("jfk-dropdown-content-show");
                activeBtn.classList.add("jfk-dropdown-btn-active");

                isDropdownActive = true;
        }

        onClickTransition = null;
}

function menu_showDropdown(e, id) {
        if (isTouchSupported && onClickTransition == null) {
                let dropdown = document.getElementById(id);

                onClickTransition = setTimeout(menu_dropdownDelayed, 100, e, dropdown);
        }
}

window.onclick = function (event) {
        if (!event.target.matches('.jfk-dropdown-btn')) {
                if (isDropdownActive && onClickTransition == null) {
                        menu_closeDropdowns();
                        isDropdownActive = false;
                }
        }

        if (typeof modal !== 'undefined') {
                if (event.target == modal) {
                        modal.style.display = "none";
                }
        }
} 

function copyURI(evt, text="Copied!") {
        evt.preventDefault();
        navigator.clipboard.writeText(evt.target.getAttribute('href')).then(() => {
          /* clipboard successfully set */
        }, () => {
          /* clipboard write failed */
        });
        const element = {target: evt.target, innerHtml: evt.target.innerHTML};
        setTimeout(function(oldHtml) {
                element.target.innerHTML = element.innerHtml;
        }, 800, element);
        evt.target.innerHTML = text;
}