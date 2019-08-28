import React from "react";
import colormap from "colormap";

// Short circuiting frame comparison
const frameComp = (prev, next) => {
    if(typeof prev === 'undefined' && typeof next === 'undefined')
        return true;
    else if(typeof prev === 'undefined' || typeof next === 'undefined')
        return false;
    for (var i = 0, l=prev.length; i < l; i++) {
        // recurse into the nested arrays
        if (prev[i] instanceof Array && next[i] instanceof Array)
            if (frameComp(prev[i],next[i])) return false;
        else if (this[i] != array[i])
            return false;
    }
    return true;
}

class WaveCanvas extends React.PureComponent {
    constructor(props) {
        super(props);
        this.canvasRef = React.createRef();
        this.cm  = colormap({
            colormap: this.props.colormap,
            nshades: this.props.nshades,
            format: 'rgba',
            alpha: 1
        });

        this.draw = this.draw.bind(this);
    }

    // Assumes framedata is a normalised image between 0 and 1
    draw() {
        const canvas = this.canvasRef.current;
        const ctx = canvas.getContext("2d");
        const width = canvas.width;
        const height = canvas.height;

        // Draw Waves
        let buf = ctx.createImageData(width, height);

        for(let pos = 0; pos < buf.data.length; pos+=4) {
            const x = Math.floor(pos%width);
            const y = Math.floor(pos/width);

            const val = this.props.frameData[x][y];
            const color = cm[Math.floor((val + 0.5)*(this.props.nshades-1))];

            buf.data[pos] = color[0];
            buf.data[pos + 1] = color[1];
            buf.data[pos + 2] = color[2];
            buf.data[pos + 3] = 255;
        }

        ctx.putImageData(buf,0,0);

        // Draw coast & blocks over this;
    }

    componentDidUpdate(prevProps) {
        if(!frameComp(this.props.frameData, prevProps.frameData))
            requestAnimationFrame(this.draw);
    }

    componentDidMount() {
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
            requestAnimationFrame(fixSize);
        };
        requestAnimationFrame(fixSize);
    }

    render() {
        return (
            <canvas
                ref={this.canvasRef} id="wave-canvas"
                width={1920} height={1080}
                className={this.props.className}>
            </canvas>
        )
    }
}
export default WaveCanvas
