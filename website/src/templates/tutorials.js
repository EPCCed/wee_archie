import React, { Fragment } from "react"
import { Link } from "gatsby"

import Layout from "../components/layout"

export default ({ pageContext: {tutorials}, location }) => (
  <Layout location={location} title="Tutorials">
    <section>
      <h1>Parallel Computing Tutorials</h1>
      <p>
        Interactive tutorials introducing parallel computing concepts with Wee
        Archie!
      </p>
    </section>
      {tutorials.map(({ node }) => {
        const title = node.title || node.slug
        return (
          <Fragment key={node.slug}>
          <hr />
          <Link style={{textDecoration:'none', color:'black'}} to={node.slug}>
            <div>
              <h2 style={{color:'-webkit-link'}}>
                {title}
              </h2>
              <p>{node.date}</p>
              <p>{node.excerpt}</p>
            </div>
          </Link>
          </Fragment>
        )
      })}
  </Layout>
)
