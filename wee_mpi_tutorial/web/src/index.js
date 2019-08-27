import React from "react";
import { ServerComm } from "@wee-archie/framework";


class WeeMPIDemo extends React.Component {

    componentDidMount() {
        this.serverComm = new ServerComm("WEEMPI");
    }

    render() {
        return (
        <div id={`tutorial-${this.props.tutId}`}>
            <button onClick={() => this.serverComm.startSim(this.props.tutId)}>
                Start Demo {this.props.tutId}
            </button>
            {this.props.children}
        </div>
        )
    }
}

export default WeeMPIDemo;
