<p align="center">
  <a href="https://github.com/EPCCed/wee_archie/">
    <img alt="Wee Archie Logo" src="https://epcced.github.io/wee_archlet/images/walogo.png" />
  </a>
</p>
<h1 align="center">
  Wee Archie's Internal Webpage
</h1>

Internal webpage for hosting tutorials and interactive demos on the Wee Archie
system, created using GatsbyJS.

## Contributing
Development for the website as a whole requires some basic knowledge of Node,
React and GatsbyJS, all of which have good documentation. If you'd like to
create smaller content that is less web development and more article writing,
that is quite easy to do!

### Tutorials

These are mostly text and images, with less interactive apps. Having some
buttons to do things on Wee Archie is good, a full page application is kind of
its own thing. You can enable interaction with Wee Archie using the web
framework - see the "Wee MPI tutorials" and demos for examples.

You can write tutorials in Markdown, or use MDX if you want to use any
Javascript features in the pages. These go in `/content/tutorials` and have some
frontmatter to tell the website how to generate their pages, such as title, the
next tutorial for multi-page pieces, and whether to include it in the tutorial
index.

### Demos

For these, you create the pages in JSX (though you can embed markdown easily)
and enable integration with the framework for interaction with Wee Archie. See
the Wave Demo for a (currently partial) example.

Full Docs WIP

### Site Deployment/Local Dev
#### Locally

 - Have an up to date version of NodeJS.
 - Install the yarn package manager `npm install -g yarn`
 - In this folder, install dependencies `yarn`
 - Dev preview server: `yarn run gatsby develop`
 - Static Build: `yarn run gatsby build`

#### On Wee Archie

 - Similar to above, but it uses NVM to manage the NodeJS installation, so
 you'll need to source that config file.
 - You can then serve the static site with `yarn run gatsby serve` or you can
 use whatever other static site server you want, like `npx http-server .`
