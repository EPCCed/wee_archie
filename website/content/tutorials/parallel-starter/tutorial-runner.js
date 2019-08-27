import React from "react";
import Loadable from "react-loadable";

const TutorialRunner = Loadable({
    loader: () => import("@wee-archie/wee-mpi-tutorial"),
    loading: () => (<div>Loading...</div>)
});
export default TutorialRunner;
