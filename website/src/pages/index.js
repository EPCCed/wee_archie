import React from "react"
import { Link } from "gatsby"
import Layout from "../components/layout"

const menu = [
  {
    name: "Tutorials",
    path: "/tutorials",
    description: "Various Tutorials",
  },
  {
    name: "Demonstrations",
    path: "/demos",
    description: "Various Demos on WeeARCHIE",
  },
]

const IndexPage = () => (
  <Layout>
    {menu.map((entry, index) => (
    <Link style={{textDecoration:'none', color:'black'}} to={entry.path} key={entry.name}>
        <div>
          <h1>{entry.name}</h1>
          <p>{entry.description}</p>
        </div>
        <hr />
    </Link>
    ))}
  </Layout>
)

export default IndexPage
