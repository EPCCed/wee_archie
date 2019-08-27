import React from "react"
import Layout from "../../../components/layout"
import Loadable from 'react-loadable';
import coastlineCosts from "./coastline_costs.png"

export const frontmatter = {
    title: "Wave Demo",
    path: "/demos/waves/"
}

const LoadableWaveDemo = Loadable({
    loader: () => import("@wee-archie/wave-demo"),
    loading() {
        return <div style={{height:"1080px", textAlign:"center",
        fontSize:"2rem"}}>Loading...</div>
    },
});

class Page extends React.Component {
    render() {
        return (
        <Layout title={frontmatter.title}>
            <section>
            <h1>Your Mission</h1>
            <p> Beachville is a seaside town that has recently been
            experiencing frequent severe storms due to climate change.
            Each storm does £200,000 worth of damage to the town.
            The Mayor has decided that wave defences should be built in
            order to protect the town from the waves, however these are
            very expensive. They decide to ask ARCHER for help to determine
            the best places to build the defences to protect the town while
            minimising costs.</p>
            <p> Now it's your turn! Click on areas of the sea to place
            defences. The cost of each defence depends on the depth of the
            water at its location. Beware, you only have a fixed budget!</p>
            <p> Once you are happy with your placement, you can run a
            simulation to determine the effects of the defences on the
            waves. Can you save Beachville? Can you find a cost-efficient
            way to do so?</p>
            </section>
            <section>
            <section>
            <h1>Simulator</h1>
            <LoadableWaveDemo
                serverAddress='192.168.2.25:5001/'
                totalBudget={20000}>
            </LoadableWaveDemo>
            </section>
            <h1> Cost Map </h1>
            <img src={coastlineCosts}/>
            </section>
        </Layout>
        );
    }
}
export default Page
