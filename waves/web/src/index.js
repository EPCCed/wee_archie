import React from "react";
import { GenericUI } from "@wee-archie/framework";
import ConfigCanvas from "./config-canvas";
import WaveCanvas from "./wave-canvas";
import styles from "./style.css";
import Tar from "tar-js";
import Gzip from "gzip-js";

// Two states, one where you configure blocks, then one where you show results.
// Make some block objects, move them around, etc.
// Preserves  aspect ratio of bg image, there might be scaling - can start
// by making for fixed size
// Raise serverComm prop
const currencyOptions = {
    style: 'currency',
    currency:'GBP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
};

const budgetString = (string, locale = "en-GB", options = currencyOptions) =>
    Intl.NumberFormat(locale,options).format(string);

class WaveDemo extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            startSimulation: false,
            budgetRemaining: this.props.totalBudget,
            configFile: new Blob(),
        }

        this.refreshRate = 0.1;
        this.prevBudget = this.props.totalBudget;

        this.config = {
            depth: [],
            mask: [],
            blocks: [],
        }

    }

    updateConfig() {
        let mask = []
        // Set new mask
        let maskString = "";
        // Depth Smoothing
        let depthString = "";
        // Rescale
        // Damping
        let dampString = "";

        let configFile = new Tar();
        configFile.append("damping.dat", dampString);
        configFile.append("mask.dat", maskString);
        configFile.append("depth.dat", depthString);
        configFile = configFile.out;
        this.setState( { configFile : new Blob(Gzip.zip(configFile))} );
    }

    render() {
        return (
        <div id="wave-demo" className={`${styles.demo}`}>
            <div id="budget-display" className={styles.budgetDisplay}>
                <span>{`Budget Remaining = \
                ${budgetString(this.state.budgetRemaining)}`}
                </span>
                <span>
                {this.prevBudget - this.budgetRemaining === 0 ?
                `Previous cost = ${budgetString(this.prevBudget
                    - this.budgetRemaining)}`
                : null }
                </span>
            </div>
            <div id="wave-display" className={styles.displayBox}>
                <ConfigCanvas
                    refreshRate={this.refreshRate}
                    className={`${styles.config} \
                    ${!this.state.startSimulation ?
                        styles.visible : styles.hidden}`
                    }
                    updateConfig={blocks => {this.config.blocks = blocks}}>
                </ConfigCanvas>

                <GenericUI
                    simName="WAVE-LED"
                    serverAddress={this.props.serverAddress}
                    refreshRate={this.refreshRate}
                    configFile={this.state.configFile}
                    dataView={(fd) =>
                        <WaveCanvas frameData={fd}
                            refreshRate={this.refreshRate}
                            colormap="velocity-blue"
                            nshades={10}
                            className={`${styles.results} \
                            ${this.state.startSimulation ?
                                styles.visible : styles.hidden}`}>
                        </WaveCanvas>
                    }
                    startSimulation={this.state.startSimulation}>
                </GenericUI>
            </div>

            <button onClick={() => {
                this.updateConfig();
                // Loading Animation
                this.setState({startSimulation: true})
            }}>

            Start Simulation
            </button>
            <button onClick={() => {this.setState({startSimulation: false})}}>
            End Simulation
            </button>
        </div>
        );
    }
}

export default WaveDemo;
