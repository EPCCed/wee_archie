import React from "react"
import { graphql } from "gatsby"
import { MDXRenderer } from "gatsby-plugin-mdx"
import Layout from "../components/layout"
import { Link } from "gatsby"
import { Loadable } from "react-loadable"

export default ({
  location,
  pageContext: { tutorial },
}) => (
  <Layout location={location} title="Tutorials">
    <section>
      <h1>{tutorial.frontmatter.title ?
          tutorial.frontmatter.title : tutorial.title}</h1>
      <p>{tutorial.date}</p>
      <MDXRenderer>{tutorial.body}</MDXRenderer>
    </section>
    <section>
    <Link to={tutorial.prevSlug}> Previous </Link>
    <Link to={tutorial.nextSlug}> Next </Link>
    </section>
  </Layout>
)
