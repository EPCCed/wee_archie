import axios from "axios";

class ServerComm {
    constructor(simName, serverAddress) {
        // this.targetBase = serverAddress || 'http://192.168.2.14:5000/'; // Wee Archie 1
        this.targetBase = serverAddress || 'http://192.168.2.25:5000/'; // Wee Archie 2

        this.simName = simName;

        console.info(`Server address is ${this.targetBase}.`);
        console.info(`Server initialised for simulation ${this.simName}.`);
        this.started = false;
        this.cancelTokenSource = axios.CancelToken.source();
        this.cancelToken  = this.cancelTokenSource.token;
    }

    // configFile must be a readable Stream
    async startSim(configFile)
    {
        if(!this.started) {
            // Alternative to locally provided data configs?
            const simAddress = `${this.targetBase}simulation/${this.simName}`
            console.info(`Posting to ${simAddress}`);

            const formData = new FormData();
            formData.append('fileToUpload', new Blob([configFile]));
            return await axios.post(
                simAddress,
                formData,
                {cancelToken: this.cancelToken}
            ).then( body => {
                this.simId = body;
                this.base = `${this.targetBase}simulation/${this.simName}/${this.simId}`;
                this.dataBase = `${this.base}/data/`;
                this.started = true;
                console.info(`Simulation started with ID = ${this.simId}`);
            })
            .catch(err => { console.error(`Simulation ${this.simId} failed
                with error ${err}`) });
        } else {
            console.error(`Simulation has already started.
                Existing Simulation ID: ${this.simId}`);
        }
    }

    async getStatus() {
        if (this.started) {
            return await axios.get(this.base, {cancelToken: this.cancelToken})
            .then( body => JSON.parse(body) )
            .catch(err => {console.error(`Request failed for ${this.simId}
                with error ${err}`)});
        } else {
            console.error(`No Simulation running`);
        }
    }

    async getDataFile(fileName) {
        if(this.started) {
            return await axios.get(this.dataBase + fileName,
            {cancelToken: this.cancelToken})
            .catch( err => { console.error(`Request failed getting \
                ${this.simId}/${fileName} with error
                ${err}`) });
        } else {
            console.error(`No Simulation running`);
        }
    }

    async deleteDataFile(fileName) {
        if(this.started) {
            return await axios.delete(this.dataBase + fileName,
            {cancelToken: this.cancelToken})
            .then( () => { console.info(`Deleted ${this.simId}/${fileName}`) })
            .catch( err => { console.error(`Request failed deleting \
                ${this.simId}/${fileName} with error
                ${err}`) });
        } else {
            console.error(`No Simulation running`);
        }
    }

    async deleteSim() {
        if(this.started) {
            return await axios.delete(this.base,
            {cancelToken: this.cancelToken})
            .then( () => { console.info(`Deleted Simulation ${this.simId}`) })
            .catch( err => { console.error(`Request failed deleting \
                ${this.simId} with error
                ${err}`) });
        } else {
            console.error(`No Simulation running`);
        }
    }

    isStarted() {
        return this.started;
    }

    cancel() {
        this.cancelTokenSource.cancel();
    }
}

export { ServerComm as default};
