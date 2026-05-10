class Timeline {
    constructor() {
        this.yearNav = document.getElementById('yearNav');
        this.yearBtns = document.querySelectorAll('.year-btn');
        this.yearSections = document.querySelectorAll('.year-section');

        if (!this.yearNav) return;

        this.init();
    }

    init() {
        this.yearBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const year = btn.dataset.year;
                this.showYear(year);
                this.setActiveButton(btn);
            });
        });
    }

    showYear(year) {
        this.yearSections.forEach(section => {
            if (section.dataset.year === year) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }

    setActiveButton(activeBtn) {
        this.yearBtns.forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Timeline();
});
