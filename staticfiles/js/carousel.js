class Carousel {
    constructor() {
        this.track = document.getElementById('carouselTrack');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.indicators = document.getElementById('carouselIndicators');

        if (!this.track) return;

        this.slides = this.track.querySelectorAll('.carousel-slide');
        this.totalSlides = this.slides.length;

        if (this.totalSlides === 0) return;

        this.currentIndex = 0;
        this.autoplayInterval = 4000;
        this.autoplayTimer = null;
        this.isHovered = false;

        this.init();
    }

    init() {
        this.prevBtn.addEventListener('click', () => this.prev());
        this.nextBtn.addEventListener('click', () => this.next());

        this.track.addEventListener('mouseenter', () => {
            this.isHovered = true;
            this.stopAutoplay();
        });

        this.track.addEventListener('mouseleave', () => {
            this.isHovered = false;
            this.startAutoplay();
        });

        if (this.indicators) {
            const indicatorBtns = this.indicators.querySelectorAll('.indicator');
            indicatorBtns.forEach((btn, index) => {
                btn.addEventListener('click', () => this.goTo(index));
            });
        }

        this.setupTouchEvents();
        this.startAutoplay();
    }

    setupTouchEvents() {
        let startX = 0;
        let endX = 0;

        this.track.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            this.stopAutoplay();
        }, { passive: true });

        this.track.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            const diff = startX - endX;

            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    this.next();
                } else {
                    this.prev();
                }
            }
            this.startAutoplay();
        }, { passive: true });
    }

    goTo(index) {
        this.currentIndex = index;
        if (this.currentIndex >= this.totalSlides) {
            this.currentIndex = 0;
        } else if (this.currentIndex < 0) {
            this.currentIndex = this.totalSlides - 1;
        }

        this.track.style.transform = `translateX(-${this.currentIndex * 100}%)`;
        this.updateIndicators();
    }

    next() {
        this.goTo(this.currentIndex + 1);
    }

    prev() {
        this.goTo(this.currentIndex - 1);
    }

    updateIndicators() {
        if (!this.indicators) return;

        const indicatorBtns = this.indicators.querySelectorAll('.indicator');
        indicatorBtns.forEach((btn, index) => {
            btn.classList.toggle('active', index === this.currentIndex);
        });
    }

    startAutoplay() {
        if (this.isHovered) return;
        this.stopAutoplay();
        this.autoplayTimer = setInterval(() => this.next(), this.autoplayInterval);
    }

    stopAutoplay() {
        if (this.autoplayTimer) {
            clearInterval(this.autoplayTimer);
            this.autoplayTimer = null;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Carousel();
});
