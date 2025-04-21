<!-- PROJECT LOGO -->
<br />
<div align="left">
  <a href="https://github.com/awerdich/llmt">
    <img src="images/CCBPictorialLogo.jpeg" alt="Logo" width="160" height="80">
  </a>

<h3 align="center">Classification of mental health facilities using Pitchbook Data</h3>

  <p align="center">
    project_description
    <br />
    <a href="https://github.com/awerdich/llmt"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/awerdich/llmt">View Demo</a>
    &middot;
    <a href="https://github.com/awerdich/llmt/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/awerdich/llmt/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

*Introduction:* There is growing interest among policymakers to understand trends in private equity ownership of US health care facilities. Zhu et al. and Thornburg et al. have quantified penetration and acquisition trends among behavioral health facilities by private equity firms. However, no research to date has assessed the impact of ownership status on mental health access, quality, spending, or patient outcomes. Therefore, this study proposes to create a database of private equity transactions involving behavioral health facilities from 2010-2024 using Pitchbook data. 

*Data:* We have access to mergers and acquisitions data from PitchBoook, Inc., which is a company that tracks private equity deal data. The data allow users to search via keywords and categories to identify mergers/acquisitions and companies of interest. We have identified both inpatient and outpatient facilities that are listed in Pitchbook and likely private-equity related. For example, the outpatient facility data include 2,797 companies and 5,824 deals from 2010-2024. The data frame of inpatient facility data are of similar size. Each row in the data represent a company or deal, and the data include a description of the company/deal in addition to a URL.

*LLM-based classification:* The goal of this project is to evaluate the extent to which a large language model can be used to classify these transactions.  The PitchBook database contains a paragraph of text describing the transactions.  We plan to create a prompting workflow that will attempt to automatically recognize, based on these paragraphs, which deals relate to mental health facilities.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
