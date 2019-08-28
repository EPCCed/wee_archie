import React, { Fragment } from "react"
import { graphql, Link } from "gatsby"
import Layout from "../../components/layout"

export default ({ data , location}) => (
  <Layout location={location} title="Demos">
    <section>
      <h1>Wee Archie Demos</h1>
      <p>
        Interactive demonstrations on Wee Archie!
      </p>
    </section>
    {data.allJavascriptFrontmatter.edges.map(({ node: { frontmatter } }) => {
      return (
        <Fragment key={frontmatter.path}>
        <Link style={{textDecoration:'none'}} to={frontmatter.path}>
          <div>
            <hr />
            <h1>
              {frontmatter.title}
            </h1>
          </div>
        </Link>
        </Fragment>
      )
    })}
  </Layout>
)
export const query = graphql`
query {
  allJavascriptFrontmatter(filter: {node: {relativePath: {regex: "/^demos\/.*/i"}}}) {
    edges {
      node {
        frontmatter {
          title
          path
        }
      }
    }
  }
}`
