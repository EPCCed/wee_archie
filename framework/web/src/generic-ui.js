import React from 'react'
import ServerComm from './server-comm.js';

/*
*  Defines a generic UI to be composed with others, providing the shell of
*  server communication with the current framework. It is passed a demo specific
*  UI, and only handles universal needs.
*/
// TODO: Error handling on invalid requests.
class GenericUI extends React.Component {
    constructor(props) {
        // props.simName - Simulation ID on server
        // props.serverAddress - Server address with port
        // props.refreshRate - How often to update frame from server
        // props.config - Configuration sent to server
        // props.dataView - Function returning component, passed frameData.
        //     frameData - The data for the current frame
        // TODO: custom Servercomm interface

        super(props);
        this.serverComm = new ServerComm(this.props.simName,
            this.props.serverAddress);

        // State the UI should care about
        this.state = {
            connStatus: "Disconnected",
            frameData: undefined,
            frameNo: 0,
        };

        // State that is just for internal processing
        this.fileNames = [];
        this.files = {};
        this.numFilesGot = 0;

        // Bind Event Handlers
        this.startSimulation = this.startSimulation.bind(this);
        this.endSimulation = this.endSimulation.bind(this);
    }

    // On First Render Methods
    componentDidMount() {
        if(this.props.startSimulation && !this.serverComm.isStarted())
            startSimulation(this.props.configFile)
        else if (this.serverComm.isStarted())
            endSimulation()

        this.timerID = setInterval(
            () => this.refresh(),
            this.props.refreshRate
        );
    }

    componentWillUnmount() {
        clearInterval(this.timerID);

        // Cancels ongoing comms on page close;
        if(this.serverComm.isStarted()) {
            this.serverComm.deleteSim().then(
                () => {this.serverComm.cancel()}
            );
        } else {
            this.serverComm.cancel();
        }
    }

    startSimulation(configFile) {
        this.serverComm.startSim(configFile);
    }

    refresh() {
        if(!this.serverComm.isStarted()) return;

        this.serverComm.getStatus().then(
            data => {
                this.setState({ connStatus: data.status });
                this.fileNames = data.fileNames;

                // Start new file downloads
                if (this.numFilesGot < this.fileNames.length) this.getData();

                // Display next data frame if downloaded, get rid of old one.
                if (frameNo < this.numFilesGot)
                    this.setState(
                        (state, props) => ({frameNo: state.frameNo + 1}),
                        () => { delete this.files[toString(state.frameNo)] }
                    );
            }
        );
    }

    // Download all new files
    async getData() {
        const start = this.numFilesGot;
        this.numFilesGot = this.fileNames.length;

        const promises = this.fileNames.slice(start).map(
            async (fname, n) => {
                console.info(`Getting frame ${fname}`);
                this.files[toString(n)] = await this.serverComm.getDataFile(fname);
            });

        return Promise.all(promises);
    }

    endSimulation() {
        this.serverComm.deleteSim();
        this.setState({
            connStatus: false
        });
    }

    render() {
        return (
            <div id={`${this.props.simName}-demo`}>
                {this.props.dataView(this.files[toString(this.state.frameNo)])}
                {this.props.children}
            </div>
        );
    }
}

export { GenericUI as default };
