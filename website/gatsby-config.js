module.exports = {
  siteMetadata: {
    title: `Wee Archie`,
    description: `Internal website for running demonstrations and viewing
    tutorials on the WeeARCHIE cluster.`,
    authors: [`Caelen Feller`],
  },
  plugins: [
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `pages`,
        path: `${__dirname}/src/pages/`,
      },
    },
    `gatsby-transformer-javascript-frontmatter`,
    {
      resolve: `gatsby-plugin-mdx`,
      options: {
        extensions: [`.mdx`, `.md`],
        gatsbyRemarkPlugins: [{
            resolve: `gatsby-remark-images`,
            options: {
              maxWidth: 1380,
              linkImagesToOriginal: false,
            },
          },
          {
            resolve: `gatsby-remark-numbered-footnotes`
          },
          {
            resolve: `gatsby-remark-smartypants`
          },
        ],
        remarkPlugins: [require(`remark-slug`)],
      }
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `tutorials`,
        path: `${__dirname}/content/tutorials/`,
      },
    },
    `gatsby-plugin-sass`,
    `gatsby-plugin-react-helmet`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
  ],
}
