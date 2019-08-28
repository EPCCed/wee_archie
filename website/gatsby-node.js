const path = require(`path`)
const crypto = require(`crypto`)

// Options
let basePath = `/`
let tutorialPath = `tutorials`

const TutorialTemplate = require.resolve(`./src/templates/tutorial`)
const TutorialsTemplate = require.resolve(`./src/templates/tutorials`)

const mdxResolverPassthrough = fieldName => async (
  source,
  args,
  context,
  info
) => {
  const type = info.schema.getType(`Mdx`)
  const mdxNode = context.nodeModel.getNodeById({
    id: source.parent,
  })
  const resolver = type.getFields()[fieldName].resolve
  const result = await resolver(mdxNode, args, context, {
    fieldName,
  })
  return result
}

exports.sourceNodes = ({actions, schema}) => {
  const { createTypes } = actions
  createTypes(
    [
      schema.buildObjectType({
        name: `Tutorial`,
        fields: {
          id: { type: `ID!` },
          title: {
            type: `String!`,
          },
          slug: {
            type: `String!`,
          },
          nextSlug: {
            type: `String`,
          },
          prevSlug: {
            type: `String`,
          },
          date: { type: `Date`, extensions: { dateformat: {} } },
          excerpt: {
            type: `String!`,
            args: {
              pruneLength: {
                type: `Int`,
                defaultValue: 140,
              },
            },
            resolve: mdxResolverPassthrough(`excerpt`),
          },
          body: {
            type: `String!`,
            resolve: mdxResolverPassthrough(`body`),
          },
        },
        interfaces: [`Node`],
      })
    ]
  )
}


exports.createPages = async ({ graphql, actions, reporter }) => {
  const { createPage } = actions

  const result = await graphql(`
    {
      site {
        siteMetadata {
          title
        }
      }
      allTutorial(
        sort: { fields: [date, title], order: DESC }
      ) {
        edges {
          node {
            id
            excerpt
            slug
            nextSlug
            prevSlug
            title
            body
            date(formatString: "MMMM DD, YYYY")
            frontmatter {
                index
                title
                next
                prev
            }
          }
        }
      }
    }
  `)

  if (result.errors) {
    reporter.panic(result.errors)
  }

  // Create Pages
  const {
    allTutorial,
    site: { siteMetadata },
  } = result.data
  const tutorials = allTutorial.edges
  const { title: siteTitle } = siteMetadata

  // Create a page for each Tutorial
  tutorials.forEach(({ node : tutorial}) => {
    const { slug } = tutorial
    createPage({
      path: slug,
      component: TutorialTemplate,
      context: {
        tutorial,
        siteTitle,
      },
    })
  })
  console.log
  // Index Page
  createPage({
    path: tutorialPath,
    component: TutorialsTemplate,
    context: {
      tutorials: tutorials.filter(tutorial  => tutorial.node.frontmatter.index),
    }
  })
}

// Generate slugs, handle frontmatter
exports.onCreateNode = ({ node, actions, getNode, createNodeId }) => {
  const { createNode, createParentChildLink } = actions

  const toNodePath = (node, sourcePath) => {
    const { dir } = path.parse(node.relativePath)
    return path.join(basePath, sourcePath, dir,
        node.name === "index" ? "" : node.name)
  }

  const namePath = (slug, node, sourcePath) => {
    const { dir } = path.parse(node.relativePath)
    return path.join(basePath, sourcePath, dir, slug)
  }

  // Make sure it's an MDX node
  if (node.internal.type !== `Mdx`) {
    return
  }
  // Create source field (according to contentPath)
  const fileNode = getNode(node.parent)
  const source = fileNode.sourceInstanceName

  if (source === tutorialPath) {
    const slug = toNodePath(fileNode, source)

    const nextSlug = typeof node.frontmatter.next !== 'undefined' ?
        namePath(node.frontmatter.next, fileNode, source) :
        namePath("..",fileNode,source)
    const prevSlug = typeof node.frontmatter.prev !== 'undefined' ?
        namePath(node.frontmatter.prev, fileNode, source) :
        namePath("..",fileNode,source)

    const postType = source === tutorialPath ? "Tutorial" : "File"
    const fieldData = {
      title: node.frontmatter.title,
      slug,
      nextSlug,
      prevSlug,
      date: node.frontmatter.date,
      frontmatter: node.frontmatter
    }
    createNode({
      ...fieldData,
      id: createNodeId(`${node.id} >>> ${postType}`),
      parent: node.id,
      children: [],
      internal: {
        type: postType,
        contentDigest: crypto
          .createHash(`md5`)
          .update(JSON.stringify(fieldData))
          .digest(`hex`),
        content: JSON.stringify(fieldData),
        description: `${postType}s`,
      },
    })
    createParentChildLink({ parent: fileNode, child: node })
  }
}
