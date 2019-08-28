import React from "react";
import coastlineImg from "../img/coastline_nocost.png";
import coastlineCostImg from "../img/coastline_costs.png";

class ConfigCanvas extends React.PureComponent {
    constructor(props) {
        super(props);
        this.canvasRef = React.createRef();

        this.blocks = [];
        this.startX = 0;
        this.startY = 0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.dragok = false;
        this.bg = new Image();

        this.draw = this.draw.bind(this);
    }

    // Assumes framedata is a normalised image between 0 and 1
    draw() {
        const canvas = this.canvasRef.current;
        const ctx = canvas.getContext("2d");
        const dpi  = typeof window !== `undefined` ?
            window.devicePixelRatio : null;
        const ratio = canvas.height/canvas.width;

        const fixSize = () => {
            const width = Math.floor(getComputedStyle(canvas)
            .getPropertyValue('width').slice(0,-2) * dpi);
            canvas.setAttribute('width', width);
            canvas.setAttribute('height', Math.floor(width * ratio));
        };
        fixSize();

        const width = canvas.width;
        const height = canvas.height;

        ctx.fillstyle = "#FAF7F8";
        ctx.clearRect(0, 0, width, height);

        ctx.drawImage(this.bg,0,0,width,height);

        this.blocks.forEach(b => {
            ctx.fillstyle = b.fill;
            ctx.fillRect(b.x, b.y, b.width, b.height);
            ctx.fill();
        });
    }

    componentDidMount() {
        const canvas = this.canvasRef.current;
        window.addEventListener("resize", this.draw);

        this.bg.src = coastlineCostImg;
        this.bg.onload = () => this.draw();

        const getOffset = () => {
            const BB = canvas.getBoundingClientRect();
            this.offsetX = BB.left;
            this.offsetY = BB.top;
        }

        canvas.onmousedown = (e) => {
            e.preventDefault();
            e.stopPropagation();
            getOffset();

            if(this.bg.src !== coastlineImg) this.bg.src = coastlineImg;

            const mx = parseInt(e.clientX - this.offsetX);
            const my = parseInt(e.clientY - this.offsetY);

            // test each block to see if mouse is inside
            this.dragok = false;
            this.blocks.forEach( b => {
                if (mx > b.x && mx < b.x + b.width
                    && my > b.y && my < b.y + b.height) {
                    this.dragok = true;
                    b.isDragging = true;
                }
            });

            if(!this.dragok)
            {
                this.blocks.push({
                    x: mx - 10,
                    y: my - 5,
                    width: 10,
                    height: 5,
                    fill: "#000000",
                    isDragging: true
                });
                this.dragok=true;
            }

            this.draw();

            // Ensure configFile is up to date
            this.props.updateConfig(this.blocks);

            // save the current mouse position
            this.startX = mx;
            this.startY = my;
        };

        canvas.onmouseup = (e) => {
            e.preventDefault();
            e.stopPropagation();

            getOffset();

            // clear all the dragging flags
            this.dragok = false;
            this.blocks.forEach( b => {
                b.isDragging = false;
            });
        };

        canvas.onmousemove = (e) =>{
            if (this.dragok) {
                getOffset();
                // tell the browser we're handling this mouse event
                e.preventDefault();
                e.stopPropagation();

                // get the current mouse position
                const mx = parseInt(e.clientX - this.offsetX);
                const my = parseInt(e.clientY - this.offsetY);

                // calculate the distance the mouse has moved
                const dx = mx - this.startX;
                const dy = my - this.startY;

                // move each rect that isDragging
                this.blocks.forEach( b => {
                    if (b.isDragging) {
                        b.x += dx;
                        b.y += dy;
                    }
                });

                // redraw the scene with the new rect positions
                this.draw();

                // reset the starting mouse position for the next mousemove
                this.startX = mx;
                this.startY = my;

                // Ensure configFile is up to date
                this.props.updateConfig(this.blocks);
            }
        };
    }

    componentWillUnmount() {
        window.removeEventListener("resize", this.draw);
    }

    render() {
        return (
            <canvas
                ref={this.canvasRef} id="wave-demo-config"
                width={1920} height={1080}
                className={this.props.className}>
            </canvas>
        )
    }
}

export default ConfigCanvas;
