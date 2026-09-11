# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "altair==6.2.2",
#     "pandas==3.0.5",
#     "cwsandbox==0.24.0",
#     "marimo>=0.23.8",
#     "openai==2.46.0",
#     "wandb[sandbox]==0.27.0",
#     "wanderland==0.1.2",
#     "weave==0.52.38",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    css_file="/usr/local/_marimo/custom.css",
    auto_download=["html"],
)

with app.setup(hide_code=True):
    import marimo as mo
    import random
    import ast
    import html
    import json
    import os
    import re
    import time
    import weave
    import openai

    from wandb.sandbox import (
        Sandbox, SandboxDefaults, ResourceOptions,
        SandboxCommandTimeoutError, SandboxExecutionError, SandboxError,
    )

    import wanderland as bp
    from wanderland import move_forward, turn_left, turn_right, collect_gem


@app.cell(hide_code=True)
def intro():
    mo.md("""
    # Can LLMs plan?

    ![alt](https://raw.githubusercontent.com/ktaletsk/coreweave-hacks-demo/main/assets/can-llms-plan-banner.avif)

    This demo explores the ability of models to reason about gridworld puzzles and solve thwem

    First, write a plan for **Mo the Mossball** yourself. Then give a language
    model the same kind of world and ask it to plan—with thinking off and on.
    Finally, ask the model to **write a planner** and run that Python in a Sandbox.

    Wanderland gives us a world we can see, play and check. W&B Inference supplies
    the models, Serverless Sandbox runs their code, and Weave records the calls.
    """)
    return


@app.cell(hide_code=True)
def marimo_widgets_feature():
    # Official wordmark: https://marimo.io/logotype-wide.svg
    # Documentation: https://docs.marimo.io/guides/interactivity/
    marimo_widgets_card = mo.Html(r"""<style>
    .cw-marimo-widgets-card {
      box-sizing: border-box; display: flex; flex-direction: column; align-items: center;
      gap: 6px; width: 180px; height: 244px; max-width: 100%; padding: 16px; margin-left: auto;
      background: #fff; border: 1px solid #202623; border-radius: 8px;
      box-shadow: -6px 6px 0 #56b5a7;
      color: #202623 !important; text-align: center; text-decoration: none !important;
      font-family: ui-sans-serif, system-ui, sans-serif;
      transition: transform .2s, box-shadow .2s;
    }
    .cw-marimo-widgets-card:hover {transform: translateY(-4px); box-shadow: -6px 10px 0 #56b5a7;}
    .cw-marimo-widgets-card:focus-visible {outline: 3px solid #09988b; outline-offset: 9px;}
    .cw-marimo-widgets-card svg {display: block; flex-shrink: 0;}
    .cw-marimo-widgets-card .cw-marimo-brand {display: block; width: 148px; height: 29px; object-fit: contain; margin: 0 0 5px; flex-shrink: 0;}
    .cw-marimo-widgets-card .cw-marimo-title {font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 18px; line-height: 20px; font-weight: 700;}
    .cw-marimo-widgets-card .cw-marimo-description {font-size: 13px; line-height: 17px; color: #646970;}
    .cw-marimo-widgets-card .cw-marimo-docs {font-size: 12px; line-height: 18px; color: #087e73; font-weight: 600;}
    @media (prefers-reduced-motion: reduce) {
      .cw-marimo-widgets-card {transition: none;}
    }
    </style>
    <a class="cw-marimo-widgets-card" href="https://docs.marimo.io/guides/interactivity/"
       target="_blank" rel="noopener noreferrer" aria-label="marimo Interactive widgets documentation">
      <img class="cw-marimo-brand" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgd2lkdGg9IjMwNi40NTkwMSIKICAgaGVpZ2h0PSIxMDEuNjI1IgogICB2aWV3Qm94PSIwIDAgMjI5Ljg0NDI1IDc2LjIxODc0MyIKICAgdmVyc2lvbj0iMS4xIgogICBpZD0ic3ZnMTU2OCIKICAgc29kaXBvZGk6ZG9jbmFtZT0ibG9nb3R5cGUtd2lkZS5zdmciCiAgIGlua3NjYXBlOnZlcnNpb249IjEuMi4yIChiMGE4NDg2NTQxLCAyMDIyLTEyLTAxKSIKICAgeG1sbnM6aW5rc2NhcGU9Imh0dHA6Ly93d3cuaW5rc2NhcGUub3JnL25hbWVzcGFjZXMvaW5rc2NhcGUiCiAgIHhtbG5zOnNvZGlwb2RpPSJodHRwOi8vc29kaXBvZGkuc291cmNlZm9yZ2UubmV0L0RURC9zb2RpcG9kaS0wLmR0ZCIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8ZGVmcwogICAgIGlkPSJkZWZzMTU3MiIgLz4KICA8c29kaXBvZGk6bmFtZWR2aWV3CiAgICAgaWQ9Im5hbWVkdmlldzE1NzAiCiAgICAgcGFnZWNvbG9yPSIjZmZmZmZmIgogICAgIGJvcmRlcmNvbG9yPSIjMDAwMDAwIgogICAgIGJvcmRlcm9wYWNpdHk9IjAuMjUiCiAgICAgaW5rc2NhcGU6c2hvd3BhZ2VzaGFkb3c9IjIiCiAgICAgaW5rc2NhcGU6cGFnZW9wYWNpdHk9IjAuMCIKICAgICBpbmtzY2FwZTpwYWdlY2hlY2tlcmJvYXJkPSIwIgogICAgIGlua3NjYXBlOmRlc2tjb2xvcj0iI2QxZDFkMSIKICAgICBpbmtzY2FwZTpkb2N1bWVudC11bml0cz0icHQiCiAgICAgc2hvd2dyaWQ9ImZhbHNlIgogICAgIGlua3NjYXBlOnpvb209IjEuMTczNDg5NiIKICAgICBpbmtzY2FwZTpjeD0iMjkuODI1NTcyIgogICAgIGlua3NjYXBlOmN5PSIxNzUuNTQ0OCIKICAgICBpbmtzY2FwZTp3aW5kb3ctd2lkdGg9IjI1NjAiCiAgICAgaW5rc2NhcGU6d2luZG93LWhlaWdodD0iMTM3MSIKICAgICBpbmtzY2FwZTp3aW5kb3cteD0iMCIKICAgICBpbmtzY2FwZTp3aW5kb3cteT0iMzIiCiAgICAgaW5rc2NhcGU6d2luZG93LW1heGltaXplZD0iMSIKICAgICBpbmtzY2FwZTpjdXJyZW50LWxheWVyPSJzdXJmYWNlMSIgLz4KICA8ZwogICAgIGlkPSJzdXJmYWNlMSIKICAgICB0cmFuc2Zvcm09Im1hdHJpeCgwLjMyNjMzNDYzLDAsMCwwLjMyNjMzNDYzLC0xNTkuMTgzNzQsLTEyMC40NTM2MSkiPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMxYzczNjE7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmUiCiAgICAgICBkPSJtIDc2NS43MTYwMSw1OTUuNTAwMjUgaCAyMy4zMjQyMiB2IC0zMy4zMDA3OSBjIDAsLTQuODMyMDMgMi42MjUsLTcuMDM5MDYgNi4zMDA3OCwtNy4wMzkwNiAzLjg4NjcyLDAgNi4xOTkyMiwyLjIwNzAzIDYuMTk5MjIsNy4wMzkwNiB2IDMzLjMwMDc5IGggMjMuMzIwMzEgdiAtMzMuMzAwNzkgYyAwLC00LjgzMjAzIDIuNTE5NTMsLTcuMDM5MDYgNi4zMDQ2OSwtNy4wMzkwNiAzLjk5MjE4LDAgNi4zMDA3OCwyLjIwNzAzIDYuMzAwNzgsNy4wMzkwNiB2IDMzLjMwMDc5IGggMjMuNDI1NzggdiAtMzcuODE2NDEgYyAwLC0xNy4zMzU5NCAtOS4xMzY3MiwtMjMuMTEzMjggLTIwLjQ4NDM4LC0yMy4xMTMyOCAtOS44NzUsMCAtMTUuOTY4NzUsNS42NzU3OCAtMTcuNDM3NSwxMC45MjU3OCBoIC0wLjgzOTg0IGMgLTMuNTc0MjIsLTguMTkxNDEgLTguODI0MjIsLTEwLjkyNTc4IC0xNi41OTc2NiwtMTAuOTI1NzggLTguMzAwNzgsMCAtMTQuMTgzNTksNC45Mzc1IC0xNS42NTIzNCw5Ljk4MDQ3IGggLTAuODM5ODQgdiAtOC40MDIzNSBoIC0yMy4zMjQyMiB6IG0gMTAyLjUzMTI1LC0yOS42MjUgYyAwLDE4LjI4MTI1IDEwLjgyMDMxLDMxLjIwMzEyIDI2LjI2MTcyLDMxLjIwMzEyIDcuOTg0MzcsMCAxNC4xODM1OSwtMy40Njg3NSAxNi44MDg1OSwtOS45ODA0NyBoIDAuNzM0MzcgdiA4LjQwMjM1IGggMjMuMTEzMjkgdiAtNTkuMzUxNTcgaCAtMjMuMTEzMjkgdiA4LjQwMjM1IGggLTAuNzM0MzcgYyAtMi42MjUsLTYuNDA2MjUgLTguODI0MjIsLTkuOTgwNDcgLTE2LjgwODU5LC05Ljk4MDQ3IC0xNC40OTYxLDAgLTI2LjI2MTcyLDEyLjI5Mjk3IC0yNi4yNjE3MiwzMS4zMDQ2OSB6IG0gMzMuNzE4NzUsMTAuNjEzMjggYyAtNS43NzczNSwwIC0xMC4yOTI5NywtMy42Nzk2OSAtMTAuMjkyOTcsLTEwLjcxNDg1IDAsLTYuODI4MTIgNC40MTAxNSwtMTAuNjEzMjggMTAuMjkyOTcsLTEwLjYxMzI4IDUuNjc1NzgsMCAxMC4xOTE0LDMuNjc5NjkgMTAuMTkxNCwxMC42MTMyOCAwLDcuMDM1MTYgLTQuNTE1NjIsMTAuNzE0ODUgLTEwLjE5MTQsMTAuNzE0ODUgeiBtIDg0LjA0Mjk3LC0xNS4wMjM0NCB2IC0yNi44OTQ1MyBjIC05LjI0NjEsMCAtMTUuNjUyMzUsNC45Mzc1IC0xOC44MDQ2OSwxNC43MDcwMyBoIC0wLjgzOTg1IHYgLTEzLjEyODkxIGggLTIxLjExNzE4IHYgNTkuMzUxNTcgaCAyMy4wMDc4MSB2IC0yMS40Mjk2OSBjIDAsLTguNzE4NzUgNC44MzIwMywtMTMuNDQ1MzEgMTEuODcxMDksLTEzLjQ0NTMxIDIuNjI1LDAgNC42MjExLDAuNDE3OTYgNS44ODI4MiwwLjgzOTg0IHogbSA3LjE0MDYyLDM0LjAzNTE2IGggMjMuMjE4NyB2IC01OS4zNTE1NyBoIC0yMy4yMTg3IHogbSAwLC02NS41NTA3OSBoIDIzLjIxODcgdiAtNi40MDYyNSBoIC0yMy4yMTg3IHogbSAzMy4zMDA4LDY1LjU1MDc5IGggMjMuMzI0MiB2IC0zMy4zMDA3OSBjIDAsLTQuODMyMDMgMi42MjUsLTcuMDM5MDYgNi4zMDA4LC03LjAzOTA2IDMuODg2NywwIDYuMTk5MiwyLjIwNzAzIDYuMTk5Miw3LjAzOTA2IHYgMzMuMzAwNzkgaCAyMy4zMjAzIHYgLTMzLjMwMDc5IGMgMCwtNC44MzIwMyAyLjUyMzQsLTcuMDM5MDYgNi4zMDQ3LC03LjAzOTA2IDMuOTkyMiwwIDYuMzAwOCwyLjIwNzAzIDYuMzAwOCw3LjAzOTA2IHYgMzMuMzAwNzkgaCAyMy40MjU3IHYgLTM3LjgxNjQxIGMgMCwtMTcuMzM1OTQgLTkuMTM2NywtMjMuMTEzMjggLTIwLjQ4NDMsLTIzLjExMzI4IC05Ljg3NSwwIC0xNS45NjQ5LDUuNjc1NzggLTE3LjQzNzUsMTAuOTI1NzggaCAtMC44Mzk5IGMgLTMuNTcwMywtOC4xOTE0MSAtOC44MjQyLC0xMC45MjU3OCAtMTYuNTk3NiwtMTAuOTI1NzggLTguMzAwOCwwIC0xNC4xODM2LDQuOTM3NSAtMTUuNjUyNCw5Ljk4MDQ3IGggLTAuODM5OCB2IC04LjQwMjM1IGggLTIzLjMyNDIgeiBtIDEzNC4xNTIzLDEuNTc4MTIgYyAxOC4yNzc0LDAgMzEuNTExNywtMTMuMDI3MzQgMzEuNTExNywtMzEuMzA0NjkgMCwtMTguODA0NjggLTEzLjIzNDMsLTMxLjIwMzEyIC0zMS41MTE3LC0zMS4yMDMxMiAtMTguMzg2NywwIC0zMS42MjExLDEyLjM5ODQ0IC0zMS42MjExLDMxLjIwMzEyIDAsMTguMjc3MzUgMTEuMTM2NywzMS4zMDQ2OSAzMS42MjExLDMxLjMwNDY5IHogbSAwLC0yMC41ODk4NCBjIC01Ljc3NzMsMCAtMTAuMjk2OSwtMy42Nzk2OSAtMTAuMjk2OSwtMTAuNzE0ODUgMCwtNi44MjgxMiA0LjQxNDEsLTEwLjYxMzI4IDEwLjI5NjksLTEwLjYxMzI4IDUuNjcxOSwwIDEwLjE4NzUsMy42Nzk2OSAxMC4xODc1LDEwLjYxMzI4IDAsNy4wMzUxNiAtNC41MTU2LDEwLjcxNDg1IC0xMC4xODc1LDEwLjcxNDg1IHogbSAwLDAiCiAgICAgICBpZD0icGF0aDE1MzEiIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNTE3LjM3MTA5LDQxMy41NTg1OSBjIDEuNTExNzIsLTEuNzgxMjUgMy4xODc1LC00LjE1NjI1IDIuMTA1NDcsLTYuMjYxNzIgNi4wNDY4OCwtMy41NjI1IDExLjM5MDYzLC04LjI2MTcxIDE1Ljc2MTcyLC0xMy43NjU2MiAtMi4zNzUsMS44OTA2MiAtNC45NjQ4NCwzLjQwMjM0IC03LjcxODc1LDQuNTg5ODQgMjAuNjc1NzgsLTIwLjQwNjI1IDUxLjc2OTUzLC0yOS42OTE0IDgwLjMyNDIyLC0yMy45Njg3NSAtMjIuOTk2MDksLTAuODYzMjggLTQ2LjQyMTg4LDUuMjM0MzggLTY1LjQyNTc4LDE4LjE5MTQxIC0xOS4wNTQ2OSwxMi45MDIzNCAtMzMuNTE5NTMsMzIuNzEwOTQgLTM5LjA3ODEzLDU1LjA1ODU5IDguNDE3OTcsLTI0LjQ1MzEyIDI2LjE3OTY5LC00NS41NTg1OSA0OC44NTE1NywtNTcuOTcyNjUgLTEuNzgxMjUsMS44MzU5MyAtMy41NjY0MSwzLjcyMjY1IC01LjM5ODQ0LDUuNTU4NTkgOC42MzY3MiwtMy41NjI1IDE2LjQ2MDk0LC04LjkwNjI1IDI1LjA0Njg3LC0xMi42MzI4MSAyNS4yMDcwMywtMTEuMDExNzIgNTUuNTQyOTcsLTYuODU1NDcgNzkuMDIzNDQsNy41MDM5IDIzLjQ4MDQ3LDE0LjM1OTM4IDQwLjM3ODkxLDM3Ljg5NDU0IDUwLjIwMzEzLDYzLjU4OTg1IDQuMzE2NCwxMS4yMjY1NiA3LjMzOTg0LDIzLjY5NTMxIDMuNTA3ODEsMzUuMDg1OTQgLTAuODYzMjgsLTE0Ljg0Mzc1IC01LjcyMjY2LC0yOS4xNDg0NCAtMTIuMDM5MDYsLTQyLjU4OTg1IC0xMC40NzI2NiwtMjIuNDAyMzQgLTI1LjQ3NjU3LC00My4zOTg0NCAtNDYuNTgyMDQsLTU2LjI0NjA5IC0yMS4xMDU0NiwtMTIuNzkyOTcgLTQ5LjAxNTYyLC0xNi4xOTUzMSAtNzAuNjA1NDYsLTQuMTU2MjUgMTEuMDY2NCwtMS4xODc1IDIyLjIzODI4LC0xLjgzNTk0IDMzLjE5NTMxLC0wLjI2OTUzIDIwLjYyMTA5LDIuOTE0MDYgMzkuNjc1NzgsMTMuNzEwOTMgNTQuMTQwNjIsMjguNjYwMTUgMTQuNDE0MDcsMTUuMDA3ODIgMjQuNDAyMzUsMzMuOTUzMTMgMzAuMjg1MTYsNTMuODcxMSA1LjcyMjY2LDE5LjQ4ODI4IDcuNjA5MzcsNDAuOTcyNjUgMC4yNjk1Myw1OS45NzI2NSAyMS40Mjk2OSwtMzQuNjU2MjUgMTcuODY3MTksLTgyLjkxMDE1IC04LjMxMjUsLTExNC4wNTg1OSAtMTAuOTU3MDMsLTEzLjAwNzgxIC0yNS4xNTYyNSwtMjIuOTk2MDkgLTQwLjQ4NDM3LC0zMC4yMjY1NiAtMTcuNzA3MDQsLTguMzEyNSAtMzcuMTQwNjMsLTEzLjExNzE5IC01Ni42Nzk2OSwtMTIuNTc4MTMgLTE5LjUzOTA2LDAuNTM5MDYgLTM5LjA4MjAzLDYuNjQwNjMgLTU0LjY3OTY5LDE4LjQwNjI1IDEyLjk1MzEzLC0xMS40NDUzMSAyOS44NDc2NiwtMTcuOTIxODcgNDcuMDE1NjMsLTE5LjcwMzEyIDE3LjIxODc1LC0xLjcyNjU3IDM0LjY1MjM0LDEuMDgyMDMgNTEuMDExNzEsNi41ODU5MyAzNC4wMDM5MSwxMS41NTA3OSA2NC45ODgyOSwzNy4wMzEyNSA3NC45NzY1Nyw3MS41MjM0NCAyLjUzNTE1LDguODUxNTYgMy42Njc5NywxOC4wMjczNSA0LjY5NTMxLDI3LjIwNzAzIDAuODYzMjgsNy45MzM2IDEuNTY2NDEsMTUuODY3MTkgMS40MDIzNCwyMy44NTU0NyAtMC43NTM5LDM5LjQ2MDk0IC0yNS45NjQ4NCw3OC4wMDM5MSAtNjIuNzIyNjUsOTIuNDE0MDYgLTEwLjQxNzk3LDQuMDUwNzkgLTIxLjQyOTY5LDYuMjYxNzIgLTMyLjQ5NjEsNy44MjgxMyAtMTcuNzA3MDMsMi40ODA0NyAtMzYuMDU4NTksMy4yMzgyOCAtNTMuMTE3MTgsLTIuMDUwNzggLTguNzk2ODgsLTIuNzUzOTEgLTE3LjAwMzkxLC03LjAxOTUzIC0yNC42MTMyOSwtMTIuMjUzOTEgLTMxLjUyMzQzLC0yMS41OTM3NSAtNTEuNDQxNCwtNTkuMjE0ODQgLTUxLjQ0MTQsLTk3LjQzMzU5IDAsLTYuODAwNzggMC41OTM3NSwtMTMuNTQ2ODggMS41MTE3MiwtMjAuMjQyMTkgMC44MDg1OSwtNi4xNTIzNCAxLjg4NjcyLC0xMi4yNTM5MSAzLjY2Nzk3LC0xOC4xOTE0MSAyLjY5OTIxLC04Ljc0NjA5IDYuOTEwMTUsLTE3LjAwMzkgMTIuNDcyNjUsLTI0LjI4OTA2IDAuOTY4NzUsLTAuNTkzNzUgMS45NDE0MSwtMS4yNDIxOSAyLjg1OTM4LC0xLjg5MDYyIC0xMi43OTI5NywyNy4wNDI5NyAtMjAuNDA2MjUsNTkgLTguNjkxNDEsODYuNTgyMDMgLTQuMjEwOTQsLTE3Ljk3MjY2IC00LjQ4MDQ3LC0zNi44MTI1IC0wLjc1MzkxLC01NC44NDM3NSAxLjE4NzUsLTAuNDI5NjkgMi4zNzUsLTAuOTE0MDYgMy41MDc4MiwtMS40MDIzNSAwLjA1NDcsLTEuMTg3NSAwLjEwNTQ3LC0yLjMyMDMxIDAuMTYwMTUsLTMuNTA3ODEgLTAuODYzMjgsMC45NzI2NiAtMS42NzE4NywxLjk0MTQxIC0yLjUzNTE1LDIuODU5MzggMS45OTYwOSwtMTQuMzA0NjkgOC4xNDg0MywtMjcuODUxNTcgMTcuMzc4OSwtMzguODA4NiBtIDguNjkxNDEsLTAuNzAzMTIgYyAzLjM0NzY2LC0yLjI2NTYzIDYuNjk1MzEsLTQuNTM1MTYgMTAuMDQyOTcsLTYuODAwNzggLTIuMTA1NDcsNC4yNjU2MiAtNS45OTIxOSw3LjYwOTM3IC0xMC41MjczNSw5LjEyMTA5IC0yMS4wNTA3OCwyMS43NTM5MSAtMjcuNTMxMjUsNTQuMTk1MzEgLTI1LjA0Njg3LDg0LjMxNjQxIDAuOTcyNjYsMTEuMzkwNjIgMy4yOTI5NywyMy4yMTA5MyAxMC42MzI4MSwzMS45NTcwMyAtNS4xMjUsLTIxLjA1NDY5IC01LjM5ODQ0LC00My4yOTI5NyAtMC42OTkyMiwtNjQuNDUzMTMgMC45MTc5NywtMC4wNTQ3IDEuMjM4MjgsMS4xMzI4MiAxLjIzODI4LDIuMDUwNzggMC4zNzg5MSwxNC4xOTkyMiAtMi4wNTA3OCwyOC4zOTQ1NCAtMS4wMjM0Myw0Mi41ODk4NSAxLjAyMzQzLDE0LjE0NDUzIDYuMzE2NCwyOS4wOTc2NSAxOC4xOTE0LDM2LjgxNjQgOS4yODUxNiw2LjA0Mjk3IDE4LjUxNTYzLDEyLjA4OTg1IDI3Ljc0NjEsMTguMTM2NzIgLTIxLjU5Mzc1LC02LjkxMDE1IC00MC40MzM2LC0yMS45MTc5NyAtNTIuMDg5ODUsLTQxLjM0NzY1IDMuMTI4OTEsOC40NzI2NSA3LjUsMTYuNTE1NjIgMTIuODk4NDQsMjMuNzUgLTAuNjk5MjIsLTEuOTQ1MzIgLTEuMzQ3NjYsLTMuOTQxNDEgLTIuMDUwNzgsLTUuOTM3NSA1LjQ1MzEyLDUuMTI4OSAxMC45NTcwMywxMC4xNDg0MyAxNi40MTAxNiwxNS4yMjI2NSAzLjk5NjA5LDMuNzIyNjYgMTAuMjU3ODEsNy41IDE0LjM1OTM3LDMuOTM3NSAwLjY0ODQ0LDEuMzUxNTcgLTAuNTM5MDYsMy4wMjM0NCAtMS45OTYwOSwzLjQwMjM1IC0xLjQ2MDk0LDAuNDMzNTkgLTMuMDIzNDQsMCAtNC40ODA0NywtMC40MzM2IDYuNTMxMjUsNC42OTkyMiAxMy4zMzIwMyw5LjAxNTYzIDIwLjM0NzY1LDEyLjk1NzAzIC0xLjAyMzQzLDAuMTYwMTYgLTEuMzQ3NjUsMS42NzE4OCAtMC42OTkyMSwyLjUzNTE2IDAuNjQ0NTMsMC44NjcxOSAxLjcyNjU2LDEuMDgyMDMgMi43NSwxLjM1MTU2IDI1Ljc1LDUuNTU4NiA1My4xNzE4NywzLjUwNzgyIDc3Ljc4NTE1LC01Ljk5MjE4IC0yMS4xNjAxNSw0Ljk2NDg0IC00My43MjI2NSw2LjEwMTU2IC02NC4yMzQzNywtMS4wNzgxMyAtMTcuMzI4MTMsLTYuMDQ2ODcgLTMyLjQ5NjEsLTE3Ljk3NjU2IC00Mi40Mjk2OSwtMzMuMzU5MzcgLTMuMTgzNTksLTQuOTY4NzUgLTUuODI4MTMsLTEwLjIwMzEzIC04LjI1NzgxLC0xNS41NDY4OCAtNy44MjgxMywtMTcuNTk3NjYgLTEyLjc5Mjk3LC0zNi44MTI1IC0xMS4zOTA2MywtNTYuMDMxMjUgMS40MDYyNSwtMTkuMjE0ODQgOS44MjQyMiwtMzguMzc4OTEgMjQuOTQxNDEsLTUwLjI1MzkxIDEuNTYyNSwtMS4yNDIxOCAzLjUwNzgxLC0yLjQyOTY4IDUuNDQ5MjIsLTEuOTQ1MzEgLTE0Ljg5ODQ0LDEwLjc5Njg4IC0yMy43NSwyOC42NjQwNiAtMjYuMDcwMzIsNDYuOTEwMTYgLTIuMzIwMzEsMTguMjk2ODcgMS40NTcwNCwzNi44NjcxOSA4LjA5NzY2LDU0LjAzMTI1IDQuNzUsMTIuMTQ4NDQgMTEuMDYyNSwyMy45MTQwNiAxOS43NTM5MSwzMy42Mjg5IDMuNzI2NTYsNC4xNTYyNSA3LjkzNzUsNy45Mzc1IDEyLjczODI4LDEwLjc5Njg4IDguODAwNzgsNS4yODkwNiAxOS4yMTg3NSw3LjI4OTA2IDI5LjQyMTg3LDguNTgyMDMgMTMuODcxMSwxLjc4MTI1IDI3Ljg1MTU3LDIuNTM5MDYgNDEuODMyMDMsMi4yMTQ4NCAtMTcuNjUyMzQsNC4xNTYyNSAtMzYuMTEzMjgsMS4xODc1IC01My45ODA0NiwtMS43ODEyNSAzMC4zMzk4NCwxMS4zOTA2MyA2NS45MTAxNSw0LjQyNTc5IDkxLjk4NDM3LC0xNC43MzgyOCA1LjE3OTY5LC0zLjgzMjAzIDEwLjA5Mzc1LC04LjA5Mzc1IDE0LjAzMTI1LC0xMy4yMjI2NSA2LjA0Njg4LC03Ljg4MjgyIDkuNjY0MDYsLTE3LjQ4ODI4IDExLjUsLTI3LjI2MTcyIDQuNzUsLTI1LjQ3NjU2IC0yLjA1MDc4LC01Mi4wODk4NSAtMTQuNDE0MDYsLTc0LjkyMTg4IC04LjU4MjAzLC0xNS44NzEwOSAtMTkuOTcyNjYsLTMwLjU1MDc4IC0zNC45NzY1NiwtNDAuNTM5MDYgLTE0LjAzNTE2LC05LjI4NTE2IC0zMC43MTQ4NSwtMTQuMTk1MzEgLTQ3LjUwMzkxLC0xNS4xMTMyOCAtMjUuODAwNzgsLTEuNTExNzIgLTUzLjExMzI4LDcuMDE1NjIgLTcwLjI4MTI1LDI2LjQ0OTIyIE0gNTc2Ljc1LDU4OC4xNzk2OSBjIDExLjYwNTQ3LDIuOTE0MDYgMjMuMzIwMzEsNS4wMTk1MyAzNS4xOTUzMSw2LjQyNTc4IC0xNC41NzQyMiwzLjM0Mzc1IC0yOS41ODIwMywtMS43ODEyNSAtNDMuNjY3OTcsLTYuODAwNzggLTguMzE2NCwtMi45MTc5NyAtMTYuNzM0MzcsLTUuOTQxNDEgLTI0LjQ1MzEyLC0xMC4yNTc4MiAtMTguNjc5NjksLTEwLjM2MzI4IC0zMi43MTQ4NSwtMjguMTI1IC00MC44NjMyOCwtNDcuODc4OSAtMS40MDIzNSwtMy41MDc4MSAtMi42OTkyMiwtNy4wMTk1MyAtMy43NzczNSwtMTAuNTgyMDMgLTAuMTA5MzcsLTAuNDI5NjkgLTAuNDMzNTksMC41OTM3NSAwLDAuMzc4OSAwLjQyOTY5LC0wLjE2MDE1IDAuMzc1LC0wLjgwODU5IDAuMTYwMTYsLTEuMjQyMTggLTQuODU5MzgsLTExLjcxMDk0IC03LjgyODEzLC0yNC4yODkwNyAtOC43NDYwOSwtMzYuOTIxODggLTAuOTE3OTcsMTkuMTA5MzggMy44MzIwMywzOC4zMjQyMiAxMi40Njg3NSw1NS40Mzc1IDkuMzk0NTMsMTguNjIxMDkgMjMuNDg0MzcsMzQuOTgwNDcgNDEuMTg3NSw0Ni4wNDI5NyAxNy42NTIzNCwxMS4wNjY0MSAzOC45MTc5NiwxNi42Nzk2OSA1OS42NDg0MywxNC42ODM1OSAyOS4xNDg0NCwtMi44NTkzNyA1NC43MzQzOCwtMTkuODYzMjggNzguMjE0ODUsLTM3LjMwMDc4IC0xMC4zNjMyOCwxMy43MTA5NCAtMjYuMDcwMzIsMjIuMTg3NSAtNDEuMzQ3NjYsMzAuMTc1NzggMjYuMzk0NTMsLTcuMzk0NTMgNDcuNTU0NjksLTI4LjI4NTE1IDYwLjI5Njg4LC01Mi41NzQyMiAtNi4zMTY0MSwxMC43OTI5NyAtMTYuMTk1MzIsMTkuMjY5NTQgLTI2LjkzNzUsMjUuNjM2NzIgLTEwLjc5Njg4LDYuMzcxMSAtMjIuNjE3MTksMTAuNzk2ODggLTM0LjQzNzUsMTUuMDYyNSAtNS4xODM2LDEuODkwNjMgLTEwLjQxNzk3LDMuNzIyNjYgLTE1Ljc2MTcyLDUuMjM0MzggLTE1LjI3NzM1LDQuMzc1IC0zMS4zNjMyOCw1Ljg4NjcyIC00Ny4xNzk2OSw0LjQ4MDQ3IG0gMTA3Ljk1NzAzLC0zNi40ODgyOCBjIDIuNjk5MjIsLTIuNTM5MDcgNS4zNDc2NiwtNS4xMjg5MSA3LjUwMzkxLC04LjA0Mjk3IDMuNDAyMzQsLTQuNjk1MzIgNS42Njc5NywtMTAuMTQ4NDQgNy44MjgxMiwtMTUuNTQ2ODggMi45MTQwNiwtNy4zMzk4NCA1Ljg4MjgxLC0xNC43MzgyOCA2LjY0MDYzLC0yMi42MTcxOSAtMS40MDYyNSwxLjI0MjE5IC0xLjg5MDYzLDMuMDc4MTMgLTIuNDI5NjksNC44NTkzOCAtNy4xNzk2OSwyNC44ODI4MSAtMjQuOTM3NSw0Ni41ODIwMyAtNDcuOTg4MjgsNTguNDU3MDMgMTAuODUxNTYsLTIuNDI5NjkgMjAuMTg3NSwtOS41IDI4LjQ0NTMxLC0xNy4xMDkzNyBtIC0xMzEuOTIxODcsMjYuNDQ5MjEgYyAxLjEzMjgxLDAuMjY5NTQgMi41MzUxNSwwLjc1MzkxIDIuNTg5ODQsMS44OTA2MyAwLjQyOTY5LC0wLjc1NzgxIDEuNzI2NTYsLTAuNzU3ODEgMi4yMTA5NCwwIDAuMjE4NzUsLTAuMDU0NyAwLjA1NDcsLTAuNDMzNTkgLTAuMjE0ODUsLTAuNTQyOTcgLTEuNjE3MTgsLTAuODYzMjggLTMuMjM4MjgsLTEuNzI2NTYgLTQuODA0NjgsLTIuNTg5ODQgLTYuNTMxMjUsLTMuNTA3ODIgLTEyLjUyMzQ0LC03Ljg3ODkxIC0xNy44NjcxOSwtMTIuOTUzMTMgLTAuNjQ4NDQsMS40MDIzNSAtMC4xNjAxNiwzLjE4MzYgMS4wODIwMyw0LjA0Njg4IDIuMzc1LDEuNzI2NTYgNC43NSwzLjQ1MzEyIDcuMTI1LDUuMTgzNTkgMi44NTkzNywyLjM3NSA2LjI2MTcyLDQuMTAxNTYgOS44Nzg5MSw0Ljk2NDg0IG0gMTU1Ljg5MDYyLC04MS42MTcxOCBjIC0wLjIxNDg0LDMuOTk2MDkgLTAuNDMzNTksOC4wNDI5NyAtMC43MDMxMiwxMi4wMzkwNiAtMC4wNTA4LDAuNTM5MDYgLTAuMDUwOCwxLjA3ODEyIC0wLjA1MDgsMS42MTcxOSAtMC4wNTQ3LDAuOTcyNjUgLTAuMTA5MzcsMS45NDUzMSAtMC4yMTg3NSwyLjg2MzI4IC0wLjA1NDcsMS4xODc1IC0wLjEwNTQ2LDIuMjY1NjIgLTAuMTA1NDYsMy40NTMxMiAyLjI2NTYyLC05LjE3NTc4IDMuMDc0MjEsLTE4Ljc4NTE1IDIuMzc1LC0yOC4xNzU3OCAtMC4yNjk1NCwtMC4xMDkzNyAtMC41NDI5NywtMC4yNjk1MyAtMC43NTc4MiwtMC40MzM1OSAtMC4xNjAxNSwyLjg1OTM3IC0wLjM3ODksNS43MjI2NSAtMC41MzkwNiw4LjYzNjcyIG0gLTIwOS44MTY0LC01OS4xNjAxNiBjIC0wLjM3ODksMC42OTkyMiAtMC43MDMxMiwxLjQwMjM0IC0xLjAyNzM0LDIuMTA1NDcgMC4zNzg5MSwwLjQ4NDM3IDEuMDc4MTMsLTAuMTA5MzggMS4yNDIxOSwtMC43MDMxMyAwLjE2MDE1LC0wLjUzOTA2IDAuMzI0MjIsLTEuMjk2ODcgMC45MTc5NywtMS4zNDc2NSAtMC4yNjk1MywtMC4yNzM0NCAtMC41MzkwNywtMC41NDI5NyAtMC44MDg2LC0wLjgxMjUgLTAuMTA5MzcsMC4yMTg3NSAtMC4yMTg3NSwwLjUzOTA2IC0wLjEwOTM3LDAuNzU3ODEgbSAzOS4wMjczNCwtNDQuODA0NjkgYyAwLjUzOTA2LC0wLjQyOTY4IDEuMDc4MTMsLTAuODYzMjggMS42MTcxOSwtMS4zNDc2NSAtMC45MTc5NywtMC4zNzg5MSAtMi4xMDU0NywwLjEwNTQ3IC0yLjQ4MDQ3LDEuMDc4MTIgMC4yNjk1MywwLjEwOTM4IDAuNTM5MDYsMC4yMTQ4NSAwLjg2MzI4LDAuMjY5NTMgbSAxLjY3MTg4LC0yLjUzNTE1IGMgMS4xODc1LDAuMjY5NTMgMi41MzkwNiwtMC4wNTQ3IDMuNTA3ODEsLTAuODYzMjggLTEuMjM4MjgsLTAuMDU0NyAtMi40ODA0NywwLjIxNDg0IC0zLjUwNzgxLDAuODYzMjggbSAtNDIuOTY0ODUsNTQuNzg5MDYgYyAtMC4wNTQ3LC0wLjI2OTUzIC0wLjEwOTM3LC0wLjUzOTA2IC0wLjEwOTM3LC0wLjc1NzgxIC0xLjAyNzM1LDAuMzc4OSAtMS41MTE3MiwxLjc4MTI1IC0wLjkxNzk3LDIuNjk5MjIgMC4yMTQ4NCwtMC42OTkyMiAwLjUzOTA2LC0xLjM0NzY2IDEuMDI3MzQsLTEuOTQxNDEgbSAtNi4xMDE1NiwyNy41MjczNCBjIC0wLjI2OTUzLDAuMzc4OTEgLTAuMDU0NywxLjAyNzM1IDAuNDMzNTksMS4wODIwMyAwLjI2OTU0LC0wLjg2MzI4IDAuMjE0ODUsLTEuNzgxMjUgLTAuMDU0NywtMi42OTkyMSAtMC41MzkwNywwLjI2OTUzIC0wLjcwMzEzLDEuMDIzNDMgLTAuMzc4OTEsMS41MTE3MSIKICAgICAgIGlkPSJwYXRoMTUzMyIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDojMWM3MzYxO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgZD0ibSA1MjcuMDg5ODQsMzk4LjM5MDYyIGMgMC4xMDU0NywwLjE2MDE2IDAuMjE0ODUsMC4zNzUgMC4zMjQyMiwwLjUzOTA3IC0wLjQ4ODI4LDAuNjk5MjIgLTEuNDA2MjUsMS4wMjM0MyAtMi4yMTQ4NCwwLjgwODU5IDAuNDMzNTksLTAuNTkzNzUgMS4wODIwMywtMS4wMjM0NCAxLjc4MTI1LC0xLjE4NzUiCiAgICAgICBpZD0icGF0aDE1MzUiIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNTIyLjgyNDIyLDQwMS44NDM3NSBjIDAuNzU3ODEsLTAuMjY5NTMgMS41NjY0LC0wLjQzMzU5IDIuMzc1LC0wLjM3ODkxIC0wLjE2MDE2LDEuMTg3NSAtMi4xNjAxNiwxLjUxMTcyIC0yLjY0NDUzLDAuMzc4OTEiCiAgICAgICBpZD0icGF0aDE1MzciIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNTIwLjEyNSwzOTkuMzU5MzcgYyAwLjQ4ODI4LC0wLjc1MzkgMS40MDIzNCwtMS4yOTI5NiAyLjM3NSwtMS4xODc1IDAuMjE0ODQsMC41NDI5NyAwLjA1NDcsMS4xODc1IC0wLjM3ODkxLDEuNTY2NDEgLTAuNzUzOSwwLjEwOTM4IC0xLjY3MTg3LDAuMjE0ODQgLTIuMjEwOTMsLTAuMzc4OTEiCiAgICAgICBpZD0icGF0aDE1MzkiIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNjcxLjQyOTY5LDQwMi45MjE4NyBjIDAuMzI0MjIsLTAuMDUwOCAwLjY0ODQzLDAuMjY5NTQgMC41OTM3NSwwLjU5Mzc1IC0wLjA1NDcsMC4zMjQyMiAtMC40Mjk2OSwwLjU0Mjk3IC0wLjc1MzkxLDAuNDMzNiAtMC40ODgyOCwtMC41MzkwNiAtMC45NzI2NiwtMS4xMzI4MSAtMS40NTcwMywtMS43MjY1NiAwLjUzOTA2LC0wLjQzMzYgMS41MDc4MSwtMC4wNTQ3IDEuNjE3MTksMC41OTM3NSIKICAgICAgIGlkPSJwYXRoMTU0MSIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDojMWM3MzYxO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgZD0ibSA1MjQuOTg0MzcsMzk0LjkzMzU5IGMgMC4zNzg5MSwtMC40Mjk2OCAxLjEzMjgyLC0wLjQyOTY4IDEuNTY2NDEsLTAuMDU0NyAtMC43MDMxMiwwLjcwMzEyIC0xLjYyMTA5LDEuMTg3NSAtMi41OTM3NSwxLjUxMTcxIC0wLjEwNTQ3LC0wLjU5Mzc1IDAuNDMzNTksLTEuMjkyOTYgMS4wMjczNCwtMS4yNDIxOCIKICAgICAgIGlkPSJwYXRoMTU0MyIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDojMWM3MzYxO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgZD0ibSA1MTYuMTMyODEsNDQ1LjEzNjcyIGMgMC40ODQzOCwtMC43MDMxMyAxLjc4MTI1LC0wLjQzMzYgMS45NDE0MSwwLjQyOTY5IC0wLjY0ODQ0LC0wLjEwNTQ3IC0xLjM0NzY2LDAuMTA5MzcgLTEuNzgxMjUsMC41OTM3NSAtMC4yNjk1MywwLjEwOTM3IC0wLjcwMzEzLC0wLjEwNTQ3IC0wLjcwMzEzLC0wLjQyOTY5IC0wLjA1MDgsLTAuMjY5NTMgMC4yNzM0NCwtMC41OTM3NSAwLjU5Mzc1LC0wLjU0Mjk3IgogICAgICAgaWQ9InBhdGgxNTQ1IiAvPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMxYzczNjE7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmUiCiAgICAgICBkPSJtIDU0Ny4wMDc4MSw0MTAuNTg5ODQgYyAwLjI2OTUzLC0wLjEwOTM3IDAuNjQ4NDQsLTAuMjE4NzUgMC45MTc5NywtMC4xMDkzNyAwLjMyNDIyLDAuMTA5MzcgMC40ODQzOCwwLjU5Mzc1IDAuMjY5NTMsMC44MDg1OSAtMS4wMjczNCwwLjY0ODQ0IC0yLjIxNDg0LDEuMDI3MzUgLTMuNDAyMzQsMS4wODIwMyAwLjU0Mjk3LC0wLjc1NzgxIDEuMzUxNTYsLTEuMzUxNTYgMi4yMTQ4NCwtMS43ODEyNSIKICAgICAgIGlkPSJwYXRoMTU0NyIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDojMWM3MzYxO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgZD0ibSA1NjIuOTI5NjksNTc5LjI3MzQ0IGMgMC41NDI5NywwLjM3ODkgMS4xMzY3MiwwLjc1NzgxIDEuNjc1NzgsMS4xMzI4MSAtMS4xODc1LDAuNDg4MjggLTIuNTg5ODUsMC4yMTg3NSAtMy41NjI1LC0wLjY0NDUzIC0wLjIxNDg1LC0wLjM3ODkxIDAuMjE0ODQsLTAuOTE3OTcgMC41OTM3NSwtMC45MTc5NyAwLjQ4NDM3LC0wLjA1NDcgMC45MTc5NywwLjIxNDg0IDEuMjkyOTcsMC40Mjk2OSIKICAgICAgIGlkPSJwYXRoMTU0OSIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDojMWM3MzYxO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgZD0ibSA1MzguMjYxNzIsNDA1LjYyMTA5IGMgLTAuMjY5NTMsLTAuODA4NTkgLTAuMDU0NywtMS43ODEyNSAwLjU5Mzc1LC0yLjM3NSAwLjQzMzU5LC0wLjEwNTQ3IDAuODYzMjgsLTAuNDI5NjggMS4wMjczNCwtMC45MTc5NyAwLjY5OTIyLDAuMjY5NTQgMS4zNDc2NiwwLjU0Mjk3IDIuMDUwNzgsMC44MTI1IC0xLjE4NzUsMC44MDg2IC0yLjQyOTY4LDEuNjE3MTkgLTMuNjcxODcsMi40ODA0NyIKICAgICAgIGlkPSJwYXRoMTU1MSIgLz4KICAgIDxwYXRoCiAgICAgICBzdHlsZT0iZmlsbDojMWM3MzYxO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgZD0ibSA1MTEuOTIxODcsNDYzLjU5NzY2IGMgMCwtMC4zMjQyMiAwLC0wLjY0ODQ0IDAsLTAuOTcyNjYgMC41MzkwNywtMC4yNjk1MyAxLjEzMjgyLC0wLjI2OTUzIDEuNjE3MTksLTAuMDU0NyAtMC45Njg3NSwxLjAyNzM1IC0xLjUxMTcyLDIuNDI5NjkgLTEuNDAyMzQsMy44MzIwMyAtMC41OTM3NSwtMC40Mjk2OCAtMS4yNDIxOSwtMC45MTc5NyAtMS44OTA2MywtMS4zNDc2NSAwLjU0Mjk3LC0wLjQzMzYgMS4xMzY3MiwtMC45MTc5NyAxLjczMDQ3LC0xLjQwNjI1IgogICAgICAgaWQ9InBhdGgxNTUzIiAvPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMxYzczNjE7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmUiCiAgICAgICBkPSJtIDUwOC4zNTkzNyw0MTUuOTMzNTkgYyAwLjIxNDg1LC0xLjY3NTc4IDEuMTg3NSwtMy4xODc1IDIuNTM1MTYsLTQuMjEwOTMgMC4zNzg5MSwtMC4yNjk1NCAwLjk3MjY2LC0wLjQzMzYgMS4xODc1LC0wLjA1NDcgLTEuMTg3NSwxLjE4NzUgLTIuMTYwMTYsMi41MzUxNSAtMi44NTkzNyw0LjA0Njg3IC0wLjE2NDA3LDAuMjczNDQgLTAuNTkzNzUsMC40MzM2IC0wLjg2MzI5LDAuMjE4NzUiCiAgICAgICBpZD0icGF0aDE1NTUiIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNTEzLjkxNzk3LDQ0OS4zOTg0NCBjIDEuMDc4MTIsLTAuODA4NiAyLjEwNTQ3LC0xLjYxNzE5IDMuMTgzNTksLTIuNDI5NjkgLTAuMjY5NTMsMS4wMjczNCAtMC41MzkwNiwxLjk0NTMxIC0wLjgwODU5LDIuOTY4NzUgLTAuMzc4OTEsMC4yMTg3NSAtMC42NDg0NCwwLjU5NzY2IC0xLjAyMzQ0LDAuODEyNSAtMC4zNzg5MSwwLjIxNDg0IC0wLjkxNzk3LDAuMjY5NTMgLTEuMTg3NSwtMC4xMDkzOCAtMC4yMTg3NSwtMC4zNzg5IDAuMzc1LC0wLjkxNzk2IDAuNTkzNzUsLTAuNTM5MDYgLTAuMjE4NzUsLTAuMjE0ODQgLTAuNDg4MjgsLTAuNDMzNTkgLTAuNzU3ODEsLTAuNzAzMTIiCiAgICAgICBpZD0icGF0aDE1NTciIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNTU1LjA1MDc4LDQwNy41NjY0MSBjIC0wLjEwOTM3LDAuMjY5NTMgLTAuMjE0ODQsMC41MzkwNiAtMC4xMDkzNywwLjg2MzI4IC0wLjg2MzI5LDAuMTYwMTUgLTEuNjcxODgsMC4zMjQyMiAtMi40Mjk2OSwwLjQ4NDM3IC0wLjEwNTQ3LDAuMzI0MjIgLTAuMjE0ODUsMC42NDg0NCAtMC4zMjAzMSwwLjk3MjY2IC0wLjY0ODQ0LC0wLjA1NDcgLTEuMjk2ODgsLTAuMDU0NyAtMS44OTA2MywtMC4wNTQ3IC0wLjUzOTA2LC0wLjI2OTUzIDAsLTEuMDIzNDQgMC41MzkwNiwtMS4yOTI5NyAxLjA3ODEzLC0wLjU0Mjk3IDIuMjE0ODUsLTAuODY3MTkgMy40MDIzNSwtMS4wMjczNCAtMC4xNjQwNywtMC4yNjk1MyAtMC4zMjQyMiwtMC40ODQzOCAtMC40ODgyOCwtMC43NTM5MSAwLjg2MzI4LC0wLjcwMzEyIDEuODkwNjIsLTEuMTg3NSAzLjAyMzQzLC0xLjUxMTcyIDAuMjE0ODUsMC4zNzUgMC4yNjk1MywwLjgwODYgMC4xNjQwNywxLjIzODI4IC0wLjM3ODkxLDAuMTY0MDcgLTAuNzU3ODIsMC4yMTg3NSAtMS4xMzY3MiwwLjEwOTM4IDAuMDU0NywwLjI2OTUzIDAuMTA5MzcsMC41MzkwNiAwLjE2NDA2LDAuODYzMjggLTAuMzc4OTEsMC4xMDkzOCAtMC42NDg0NCwwLjE2NDA2IC0wLjkxNzk3LDAuMTA5MzgiCiAgICAgICBpZD0icGF0aDE1NTkiIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNTEyLjgzOTg0LDQxMi42NDA2MiBjIDAuNDI5NjksLTAuMjY5NTMgMS4wMjM0NCwtMC4zNzg5IDEuNTExNzIsLTAuMjY5NTMgLTAuMjE4NzUsLTAuMjY5NTMgLTAuMzc4OSwtMC41NDI5NyAtMC41NDI5NywtMC44MTI1IDAuNTQyOTcsLTAuMTA1NDcgMS4wODIwMywtMC4yMTQ4NCAxLjY3NTc4LC0wLjI2OTUzIDAuMjE0ODUsLTAuNTM5MDYgMC4yMTQ4NSwtMS4xODc1IDAsLTEuNzI2NTYgMC41OTM3NSwtMC4wNTQ3IDEuMjQyMTksMC4wNTQ3IDEuNzgxMjUsMC4yNjk1MyAwLjE2MDE2LDAuMjE0ODQgMC4yMTQ4NSwwLjUzOTA2IDAuMTYwMTYsMC44MDg1OSAtMC4yNjk1MywwLjEwOTM4IC0wLjU5Mzc1LDAuMjE4NzUgLTAuOTE3OTcsMC4zMjQyMiAtMC4xMDU0NywwLjU0Mjk3IC0wLjI2OTUzLDEuMDgyMDMgLTAuMzc1LDEuNjIxMSAtMC4yNjk1MywwLjE2MDE1IC0wLjcwMzEyLDAuMjE0ODQgLTEuMDI3MzQsMC4xMDkzNyAtMC40ODQzOCwyLjkxNDA2IC0zLjY3MTg4LDQuNTg1OTQgLTQuODA0NjksNy4yODUxNiAtMC4zNzg5MSwwLjkxNzk3IC0wLjc1MzkxLDIuMTA1NDcgLTEuNzI2NTYsMi4xMDU0NyAtMC4yNjk1MywtMC4zMjQyMiAtMC4yMTQ4NSwtMC45MTc5NyAwLjE2MDE1LC0xLjE4NzUgLTAuMzc1LC0wLjEwOTM4IC0wLjY5OTIxLC0wLjIxNDg1IC0xLjAyMzQzLC0wLjMyNDIyIC0wLjA1NDcsLTAuNTkzNzUgMC45MTc5NywtMC40Mjk2OSAxLjQwMjM0LC0wLjA1NDcgMC40MzM1OSwtMC4zNzUgMC4wNTQ3LC0xLjI0MjE5IC0wLjQ4NDM3LC0xLjI0MjE5IDAuNTkzNzUsLTAuNDg0MzcgMC45NzI2NSwtMS4yMzgyOCAxLjA3ODEyLC0xLjk5NjA5IDAuNTkzNzUsMC4wNTQ3IDEuMTg3NSwtMC4xNjAxNiAxLjU2NjQxLC0wLjU5Mzc1IC0wLjQzMzYsMC4xMDkzNyAtMC45MTc5NywtMC4yMTQ4NCAtMS4wMjczNSwtMC42OTkyMiAwLjg2MzI4LDAuMTYwMTYgMS43MzA0NywtMC42NDg0NCAxLjY3NTc4LC0xLjUxMTcyIDAuNjQ4NDQsLTAuMzc4OSAxLjI5Mjk3LC0wLjc1NzgxIDEuOTQxNDEsLTEuMTM2NzIgLTAuMjY5NTMsLTAuMTYwMTUgLTAuNjQ4NDQsLTAuNDI5NjggLTEuMDIzNDQsLTAuNjk5MjIiCiAgICAgICBpZD0icGF0aDE1NjEiIC8+CiAgICA8cGF0aAogICAgICAgc3R5bGU9ImZpbGw6IzFjNzM2MTtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZSIKICAgICAgIGQ9Im0gNjgyLjM4NjcyLDQxNS41IGMgLTEuMTg3NSwtMS42MTcxOSAtMi40Mjk2OSwtMy4xODM1OSAtMy45Mzc1LC00LjUzNTE2IC0yLjEwNTQ3LC0xLjg4NjcyIC00LjgwNDY5LC0zLjU2MjUgLTUuMjM4MjgsLTYuMzY3MTggMTIuNjg3NSwxMC43NDIxOCAyMi40NTcwMywyNC45Mzc1IDI3LjkwNjI1LDQwLjY0NDUzIDAuNDg4MjgsMC40MzM1OSAtMC4wNTA4LDEuNDA2MjUgLTAuNjQ0NTMsMS4yNDIxOCAtNC43NSwtMTAuOTU3MDMgLTEwLjg1MTU3LC0yMS40Mjk2OCAtMTguMDg1OTQsLTMwLjk4NDM3IgogICAgICAgaWQ9InBhdGgxNTYzIiAvPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMxYzczNjE7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmUiCiAgICAgICBkPSJtIDUzOS44ODI4MSw0MDYuOTcyNjYgYyAyLjIxMDk0LC0xLjc4MTI1IDQuNzUsLTMuNDU3MDQgNS42Njc5NywtNi4xNTYyNSAwLjI2OTUzLC0wLjc1MzkxIDEuMDIzNDQsLTEuMzQ3NjYgMS43MjY1NiwtMS43ODEyNSAxMC45MDIzNSwtNi44NTU0NyAyMy42NDQ1MywtMTAuNjMyODIgMzYuNDg4MjgsLTEwLjg0NzY2IC02LjQyMTg3LDEuNzI2NTYgLTEyLjc5Mjk2LDMuMzk4NDQgLTE5LjIxNDg0LDUuMTI4OTEgLTkuOTg0MzcsMi42NDQ1MyAtMTcuMzI4MTIsMTAuOTAyMzQgLTI0LjA3NDIyLDE4Ljc4NTE1IC01LjgzMjAzLDYuODU1NDcgLTExLjcxNDg0LDEzLjcxMDk0IC0xNy41NDI5NywyMC42MTcxOSAtMC43MDMxMiwxLjg5MDYyIC0xLjM1MTU2LDMuODMyMDMgLTIuMDUwNzgsNS43MjI2NiAtMC4yNjk1MywwLjg2MzI4IC0wLjU5Mzc1LDEuNzI2NTYgLTEuMzUxNTYsMi4yNjU2MiAtMC42OTkyMiwwLjU0Mjk3IC0xLjg4NjcyLDAuNTQyOTcgLTIuMzIwMzEsLTAuMjY5NTMgMi41ODk4NCwtNC41MzEyNSA1LjE4MzU5LC05LjEyMTA5IDcuODI4MTIsLTEzLjcxMDk0IDQuMjEwOTQsLTcuMTI1IDguNDE3OTcsLTE0LjQ2NDg0IDE0Ljg0Mzc1LC0xOS43NTM5IgogICAgICAgaWQ9InBhdGgxNTY1IiAvPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMxYzczNjE7c3Ryb2tlLXdpZHRoOjMyOS40MTY7ZmlsbC1vcGFjaXR5OjEiCiAgICAgICBkPSJtIDgwNy4yMDQ0NywzODQuNTE0NzggYyAtMjYuNTczNyw2MC40MzU2MyAtNDcuNDc0OSwxMjMuMTI5OCAtNzkuMTkzNSwxODEuMjc4NDUgLTQuODQxMDIsOC44NzQ4OCAtMTMuODM3OTcsMjguNzgzMyAtMjEuOTMyMjQsMzYuODc4MDEiCiAgICAgICBpZD0icGF0aDkyOCIgLz4KICA8L2c+Cjwvc3ZnPgo=" width="148" height="29" alt="marimo">
      <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60" fill="none" aria-hidden="true" focusable="false">
        <circle cx="30" cy="30" r="30" fill="#e2f4ed"/>
        <g stroke="#202623" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m25 25 7 21 4-10 10-4-21-7Z" fill="#fff"/>
          <path d="m37 37 6 6M23 15v4M15 23h4M16 16l3 3M30 17l-3 3M17 30l3-3"/>
        </g>
      </svg>
      <span class="cw-marimo-title">Interactive<br>widgets</span>
      <span class="cw-marimo-description">Interactive views,<br>connected to Python</span>
      <span class="cw-marimo-docs">Read docs <span aria-hidden="true">↗</span></span>
    </a>""")
    return (marimo_widgets_card,)


@app.cell(hide_code=True)
def act1_intro(marimo_widgets_card):
    mo.hstack([
        mo.md("""
    ## Act 1 · Meet Mo the Mossball

    This is **Mo the Mossball** (the unofficial marimo mascot), and his home is
    [Wanderland](https://github.com/ktaletsk/wanderland), the 3D coding playground
    from **Can LLMs Plan**.

    **Can you guide him to find the gems and clear the level?** Try to think
    about the plan in your head before running the code.

    Mo starts in the top-left corner, facing **east**. Walk him onto each gem's
    tile, then **collect_gem()** to pick it up. Grab both gems, then land on the
    golden ring to win. The pond in the middle is impassable, so go around.

    Type commands or tap the buttons below, one command per line.
    Your edits load into the scene automatically; press **Run My Code** to watch Mo go.
    """),
        marimo_widgets_card,
    ], align="start", widths=[0.72, 0.28], gap=1.5)
    return


@app.cell(hide_code=True)
def act1_code_state():
    get_code, set_code = mo.state(
        "move_forward()\n"
        "move_forward()\n"
        "move_forward()\n"
        "collect_gem()\n"
    )
    return get_code, set_code


@app.cell(hide_code=True)
def act1_solution_editor(get_code, set_code):
    solution_code = mo.ui.code_editor(
        value=get_code(),
        language="python",
        debounce=True,
        on_change=set_code,
        min_height=150,
        show_copy_button=False,
    )
    return (solution_code,)


@app.cell(hide_code=True)
def act1_command_buttons(get_code, set_code):
    def _appender(snippet):
        def _cb(_v):
            cur = get_code().rstrip("\n")
            set_code((cur + "\n" + snippet if cur else snippet) + "\n")
        return _cb


    def _undo_cb(_v):
        lines = get_code().rstrip("\n").split("\n")
        set_code(("\n".join(lines[:-1]) + "\n") if len(lines) > 1 else "")


    _bump = lambda v: (v or 0) + 1
    btn_forward = mo.ui.button(value=0, on_click=_bump, on_change=_appender("move_forward()"), label="move_forward()")
    btn_left = mo.ui.button(value=0, on_click=_bump, on_change=_appender("turn_left()"), label="turn_left()")
    btn_right = mo.ui.button(value=0, on_click=_bump, on_change=_appender("turn_right()"), label="turn_right()")
    btn_gem = mo.ui.button(value=0, on_click=_bump, on_change=_appender("collect_gem()"), label="collect_gem()")
    btn_undo = mo.ui.button(value=0, on_click=_bump, on_change=_undo_cb, label="\u232b undo")
    btn_clear = mo.ui.button(value=0, on_click=_bump, on_change=lambda _v: set_code(""), kind="danger", label="\u2715 clear")
    command_palette = mo.hstack(
        [btn_forward, btn_left, btn_right, btn_gem, btn_undo, btn_clear],
        justify="start", gap=0.4, wrap=True,
    )
    return (command_palette,)


@app.cell(hide_code=True)
def act1_world():
    manual_world = bp.World(bp.puzzles.gem_path())
    return (manual_world,)


@app.cell(hide_code=True)
def act1_load(manual_world, solution_code):
    _commands = {
        "move_forward": move_forward, "turn_left": turn_left,
        "turn_right": turn_right, "collect_gem": collect_gem,
    }

    def _manual_program():
        # This is the participant's editable program, as in the original notebook.
        exec(compile(solution_code.value, "<manual-plan>", "exec"), _commands)

    try:
        manual_world.load(_manual_program)
        manual_result = manual_world.result
        manual_error = None
    except Exception as _error:
        manual_world.reset()
        manual_result = None
        manual_error = f"{type(_error).__name__}: {_error}"
    return manual_error, manual_result


@app.cell(hide_code=True)
def act1_playground(
    command_palette,
    manual_result,
    manual_world,
    solution_code,
):
    _ = manual_result
    manual_scene = mo.ui.anywidget(manual_world)
    mo.hstack(
        [mo.vstack([solution_code, command_palette]), manual_scene],
        align="start", gap=1.5, widths=[0.4, 0.6],
    )
    return (manual_scene,)


@app.cell(hide_code=True)
def act1_result(manual_error, manual_scene, manual_world):
    _ = manual_scene.value
    if manual_error:
        _out = mo.callout(
            mo.md("Your code didn't run. Fix it and Mo will be ready:\n\n" + html.escape(manual_error)),
            kind="danger",
        )
    elif not manual_world.state.get("finished"):
        _out = mo.callout(mo.md("Press **Run My Code** in the scene to send Mo off."), kind="info")
    else:
        _out = mo.callout(
            mo.md(
                f"**{'Puzzle solved!' if manual_world.success else 'Keep trying…'}** "
                f"Gems: {manual_world.gems_collected}/{manual_world.total_gems} · "
                f"Goal reached: {manual_world.reached_goal}"
            ),
            kind="success" if manual_world.success else "neutral",
        )
    _out
    return


@app.cell(hide_code=True)
def act2_intro():
    mo.md("""
    ## Act 2 · Now ask a language model

    Mo's Gem Path was about the gentlest world there is. Let's generate something
    larger: irregular walls, water and lava, gems to collect, and an optional
    locked door with a matching key.

    The generator checks every candidate with Wanderland's **breadth-first search
    oracle** and rerolls worlds it cannot solve. The shortest plan gives us a
    difficulty meter. Press **Run My Code** in this scene to watch that oracle.

    Then hand a language model the **same structured world**, ask it for a plan,
    and replay its answer. Same world, same goal, same action space. Can the model?
    """)
    return


@app.cell(hide_code=True)
def world_generator():
    COLORS = ("red", "green", "blue", "purple", "yellow", "grey")

    def random_world(seed, cols, rows, gems=1, density=0.18, locked=False, attempts=500):
        """Scatter irregular walls + water + lava, drop gems and a goal, and -- when
        ``locked`` -- split the map into two rooms with a locked door + matching key.
        Every candidate is checked by the BFS oracle and rerolled if unsolvable
        (easing the obstacle density if rolls keep failing)."""
        for a in range(attempts):
            r = random.Random(seed * 100003 + a)
            d = density * (1 - a / attempts)
            actions = ["move_forward", "turn_left", "turn_right"]
            objects, walls, water, lava = {}, [], [], []

            if locked:
                # two rooms split by a wall column with a single door gap
                wc = r.randint(2, cols - 2)
                door_row = r.randint(0, rows - 1)
                walls = [(wc, w) for w in range(rows) if w != door_row]
                color = r.choice(COLORS)
                objects[(wc, door_row)] = bp.Obj("door", color, "locked")
                left  = [(c, w) for c in range(wc)         for w in range(rows) if (c, w) != (wc - 1, door_row)]
                right = [(c, w) for c in range(wc + 1, cols) for w in range(rows) if (c, w) != (wc + 1, door_row)]
                r.shuffle(left); r.shuffle(right)
                start = left.pop()
                objects[left.pop()] = bp.Obj("key", color)   # matching key in Mo's room
                goal = right.pop()
                pool = left + right
                actions += ["pickup", "toggle"]
            else:
                cells = [(c, w) for c in range(cols) for w in range(rows)]
                r.shuffle(cells)
                start, goal = cells.pop(), cells.pop()
                pool = cells

            free = []
            for cell in pool:
                t = r.random()
                if t < d:            walls.append(cell)
                elif t < d * 1.4:    water.append(cell)
                elif t < d * 1.6:    lava.append(cell)
                else:                free.append(cell)
            r.shuffle(free)
            for _ in range(min(gems, len(free))):
                objects[free.pop()] = bp.Obj("gem", blocking=False)
            if any(o.type == "gem" for o in objects.values()):
                actions.append("collect_gem")

            p = bp.Puzzle(
                name="Wildlands", cols=cols, rows=rows, start=start,
                actions=tuple(actions), heading=r.choice("NESW"),
                objects=objects, goal=goal, gaps=water, walls=walls, lava=lava,
            )
            if bp.solve(p) is not None:
                return p
        return None

    return (random_world,)


@app.cell(hide_code=True)
def gen_controls():
    gen_cols = mo.ui.slider(4, 10, value=7, label="width", show_value=True, full_width=True)
    gen_rows = mo.ui.slider(3, 8, value=6, label="height", show_value=True, full_width=True)
    gen_seed = mo.ui.slider(0, 30, value=7, label="seed", show_value=True, full_width=True)
    gen_gems = mo.ui.slider(0, 4, value=2, label="gems", show_value=True, full_width=True)
    gen_density = mo.ui.slider(0.0, 0.35, value=0.2, step=0.01, label="obstacles", show_value=True, full_width=True)
    gen_locked = mo.ui.switch(value=False, label="Doors and locks")

    # Polished control panel: a themed card (matches the paper-reference card),
    # uppercase moss-green section headers, full-width sliders with value readouts.
    _hdr = lambda t: mo.md(
        f"<span style='font-size:0.7rem;font-weight:800;letter-spacing:0.09em;"
        f"text-transform:uppercase;color:rgb(124,140,64)'>{t}</span>"
    )
    _cap = lambda t: mo.md(f"<span style='font-size:0.78rem;opacity:0.6'>{t}</span>")

    gen_controls_panel = mo.vstack([
        mo.md("**\U0001F3B2 Generator controls**"),
        _hdr("Size"),
        gen_cols,
        gen_rows,
        _hdr("Complexity"),
        gen_density,
        gen_gems,
        gen_locked,
        _hdr("Seed"),
        _cap("just variety, not difficulty"),
        gen_seed,
    ], gap=0.55).style({
        "border": "1px solid rgba(124,140,64,0.35)",
        "border-radius": "12px",
        "padding": "18px 20px",
        "background": "rgba(124,140,64,0.06)",
        "box-shadow": "0 8px 24px rgba(0,0,0,0.05)",
    })
    return (
        gen_cols,
        gen_controls_panel,
        gen_density,
        gen_gems,
        gen_locked,
        gen_rows,
        gen_seed,
    )


@app.cell(hide_code=True)
def gridworld(
    gen_cols,
    gen_density,
    gen_gems,
    gen_locked,
    gen_rows,
    gen_seed,
    random_world,
):
    gen_puzzle = random_world(
        seed=gen_seed.value, cols=gen_cols.value, rows=gen_rows.value,
        gems=gen_gems.value, density=gen_density.value, locked=gen_locked.value,
    )
    mo.stop(gen_puzzle is None, mo.callout(
        mo.md("No solvable world found. Try another seed or lower the obstacle density."), kind="warn",
    ))
    gen_env = bp.World(gen_puzzle, speed=2.0)
    gen_plan = bp.solve(gen_puzzle)
    if gen_plan is not None:
        gen_env.act(gen_plan)
    # Both model approaches receive this same generated world.
    WORLD = gen_puzzle.to_dict()
    return WORLD, gen_env, gen_plan, gen_puzzle


@app.cell(hide_code=True)
def puzzle(gen_controls_panel, gen_env, gen_plan, gen_puzzle):
    gen_world = mo.ui.anywidget(gen_env)
    mo.vstack([
        mo.hstack(
            [gen_controls_panel, gen_world],
            align="start", gap=1.5, widths=[0.4, 0.6],
        ),
        mo.callout(mo.md(
            f"**This world:** {gen_puzzle.cols} × {gen_puzzle.rows} · "
            f"{len(gen_puzzle.score_gem_cells)} gems · "
            f"{len(gen_puzzle.wall_set)} walls · {len(gen_puzzle.gap_set)} water · "
            f"{len(gen_puzzle.lava_set)} lava. "
            f"**Shortest solution: {len(gen_plan)} actions.**\n\n"
            "Grow the grid, crank the obstacles, add gems, or lock the door and watch it change."
        ), kind="info"),
    ])
    return


@app.cell(hide_code=True)
def wandb_traces_feature():
    # Official logo: https://site.wandb.ai/wp-content/uploads/2023/05/wb-cw.svg
    # Original icon and card styling: https://wandb.ai/site/inference/
    # Documentation: https://docs.wandb.ai/weave/guides/tracking/tracing
    # Inline SVG keeps the icon available without fetching a remote image.
    wandb_traces_card = mo.Html(r"""<style>
    .cw-wb-traces-card {
      box-sizing: border-box; display: flex; flex-direction: column; align-items: center;
      gap: 10px; width: 180px; max-width: 100%; padding: 16px; margin-left: auto;
      background: #20242b; border: 1px solid #4b535c; border-radius: 8px;
      color: #fff !important; text-align: center; text-decoration: none !important;
      font-family: "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
      transition: transform .2s, border-color .2s;
    }
    .cw-wb-traces-card:hover {transform: translateY(-4px); border-color: #ffcc33;}
    .cw-wb-traces-card:focus-visible {outline: 3px solid #ffcc33; outline-offset: 4px;}
    .cw-wb-traces-card svg {display: block; flex-shrink: 0;}
    .cw-wb-traces-card .cw-wb-brand {display:block; width:148px; max-width:100%; height:auto; margin:0 0 4px;}
    .cw-wb-traces-card .cw-wb-title {font-size: 20px; line-height: 26px; font-weight: 400;}
    .cw-wb-traces-card .cw-wb-description {font-size: 13px; line-height: 17px; color: #aeb3bd;}
    .cw-wb-traces-card .cw-wb-docs {font-size: 12px; line-height: 18px; color: #ffcc33; font-weight: 600;}
    @media (prefers-reduced-motion: reduce) {
      .cw-wb-traces-card {transition: none;}
    }
    </style>
    <a class="cw-wb-traces-card" href="https://docs.wandb.ai/weave/guides/tracking/tracing"
       target="_blank" rel="noopener noreferrer" aria-label="W&B Weave Traces documentation">
      <img class="cw-wb-brand" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMzYwIiBoZWlnaHQ9IjI2OSIgdmlld0JveD0iMCAwIDEzNjAgMjY5IiBmaWxsPSJub25lIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfN18yKSI+PHBhdGggZD0iTTgzMC4wNDUgMjUyLjI4M0M4MjYuNzUyIDI1Mi4yODMgODIzLjczNyAyNTEuNTQ4IDgyMS4wMDEgMjUwLjA3OUM4MTguMzE2IDI0OC42MSA4MTYuMjM5IDI0Ni41MzIgODE0Ljc2OSAyNDMuODQ3TDgxNS43NTcgMjQyLjYzMVYyNTEuMzcxSDgwOC44NDFWMTkzLjgzOUg4MTUuOTA5VjIxOS4yMjNMODE0Ljg0NSAyMTcuNDc1QzgxNi4zNjUgMjE1LjA0MyA4MTguNDQzIDIxMy4xMTggODIxLjA3NyAyMTEuNjk5QzgyMy43MTIgMjEwLjIzIDgyNi43MjcgMjA5LjQ5NSA4MzAuMTIxIDIwOS40OTVDODMzLjk3MiAyMDkuNDk1IDgzNy40MTcgMjEwLjQzMiA4NDAuNDU3IDIxMi4zMDdDODQzLjU0OCAyMTQuMTgyIDg0NS45OCAyMTYuNzQgODQ3Ljc1MyAyMTkuOTgzQzg0OS41MjcgMjIzLjE3NSA4NTAuNDEzIDIyNi44MjMgODUwLjQxMyAyMzAuOTI3Qzg1MC40MTMgMjM0LjkzIDg0OS41MjcgMjM4LjU1MiA4NDcuNzUzIDI0MS43OTVDODQ1Ljk4IDI0NS4wMzggODQzLjU0OCAyNDcuNTk2IDg0MC40NTcgMjQ5LjQ3MUM4MzcuNDE3IDI1MS4zNDYgODMzLjk0NyAyNTIuMjgzIDgzMC4wNDUgMjUyLjI4M1pNODI5LjUxMyAyNDUuNDQzQzgzMi4wOTcgMjQ1LjQ0MyA4MzQuNDAzIDI0NC44MSA4MzYuNDI5IDI0My41NDNDODM4LjQ1NiAyNDIuMjc2IDg0MC4wMjcgMjQwLjU1NCA4NDEuMTQxIDIzOC4zNzVDODQyLjMwNyAyMzYuMTQ2IDg0Mi44ODkgMjMzLjY2MyA4NDIuODg5IDIzMC45MjdDODQyLjg4OSAyMjguMDkgODQyLjMwNyAyMjUuNjA3IDg0MS4xNDEgMjIzLjQ3OUM4NDAuMDI3IDIyMS4zIDgzOC40NTYgMjE5LjU3OCA4MzYuNDI5IDIxOC4zMTFDODM0LjQwMyAyMTYuOTk0IDgzMi4wOTcgMjE2LjMzNSA4MjkuNTEzIDIxNi4zMzVDODI2LjkyOSAyMTYuMzM1IDgyNC41OTkgMjE2Ljk2OCA4MjIuNTIxIDIxOC4yMzVDODIwLjQ5NSAyMTkuNTAyIDgxOC44NzMgMjIxLjI1IDgxNy42NTcgMjIzLjQ3OUM4MTYuNDkyIDIyNS42NTggODE1LjkwOSAyMjguMTQgODE1LjkwOSAyMzAuOTI3QzgxNS45MDkgMjMzLjY2MyA4MTYuNDkyIDIzNi4xNDYgODE3LjY1NyAyMzguMzc1QzgxOC44NzMgMjQwLjU1NCA4MjAuNDk1IDI0Mi4yNzYgODIyLjUyMSAyNDMuNTQzQzgyNC41OTkgMjQ0LjgxIDgyNi45MjkgMjQ1LjQ0MyA4MjkuNTEzIDI0NS40NDNaTTg2My40MjMgMjY4LjA5MUM4NjIuNTExIDI2OC4wOTEgODYxLjU5OSAyNjguMDE1IDg2MC42ODcgMjY3Ljg2M0M4NTkuNzc1IDI2Ny43MTEgODU4LjkxNCAyNjcuNDU4IDg1OC4xMDMgMjY3LjEwM1YyNjAuNzk1Qzg1OC42NiAyNjAuODk2IDg1OS4zNDQgMjYwLjk5OCA4NjAuMTU1IDI2MS4wOTlDODYxLjAxNiAyNjEuMjUxIDg2MS44NTIgMjYxLjMyNyA4NjIuNjYzIDI2MS4zMjdDODY1LjA0NCAyNjEuMzI3IDg2Ni44NDMgMjYwLjc5NSA4NjguMDU5IDI1OS43MzFDODY5LjMyNiAyNTguNzE4IDg3MC41MTYgMjU2Ljk0NCA4NzEuNjMxIDI1NC40MTFMODc0LjIxNSAyNDguMjU1TDg3NC4wNjMgMjU0LjQxMUw4NTYuNTgzIDIxMC40MDdIODY0LjI1OUw4NzcuODYzIDI0NS4zNjdIODc1LjU4M0w4ODkuMTExIDIxMC40MDdIODk2LjkzOUw4NzguNDcxIDI1Ni4yMzVDODc3LjYxIDI1OC40MTQgODc2LjQ5NSAyNjAuMzkgODc1LjEyNyAyNjIuMTYzQzg3My44MSAyNjMuOTg3IDg3Mi4xODggMjY1LjQzMSA4NzAuMjYzIDI2Ni40OTVDODY4LjMzOCAyNjcuNTU5IDg2Ni4wNTggMjY4LjA5MSA4NjMuNDIzIDI2OC4wOTFaTTk0Ny44MyAyNTIuMjgzQzk0My44MiAyNTIuMjgzIDk0MC4xMyAyNTEuNTc0IDkzNi43MyAyNTAuMTU1QzkzMy4zOSAyNDguNjg2IDkzMC40NSAyNDYuNjM0IDkyNy45MiAyNDMuOTk5QzkyNS40MyAyNDEuMzY0IDkyMy41MSAyMzguMjc0IDkyMi4xNCAyMzQuNzI3QzkyMC43NyAyMzEuMTggOTIwLjA5IDIyNy4zMDQgOTIwLjA5IDIyMy4wOTlDOTIwLjA5IDIxOC44NDMgOTIwLjc3IDIxNC45NDIgOTIyLjE0IDIxMS4zOTVDOTIzLjUxIDIwNy44NDggOTI1LjQzIDIwNC43NTggOTI3LjkyIDIwMi4xMjNDOTMwLjQgMTk5LjQ4OCA5MzMuMzQgMTk3LjQ2MiA5MzYuNzMgMTk2LjA0M0M5NDAuMTMgMTk0LjU3NCA5NDMuODIgMTkzLjgzOSA5NDcuODMgMTkzLjgzOUM5NTEuNzMgMTkzLjgzOSA5NTUuMjIgMTk0LjUyMyA5NTguMzIgMTk1Ljg5MUM5NjEuNDYgMTk3LjI1OSA5NjQuMDkgMTk5LjAzMiA5NjYuMjIgMjAxLjIxMUM5NjguNCAyMDMuMzkgOTY5Ljk0IDIwNS43MiA5NzAuODYgMjA4LjIwM0w5NjQuMDIgMjExLjMxOUM5NjIuNyAyMDguMTc4IDk2MC42NSAyMDUuNjQ0IDk1Ny44NiAyMDMuNzE5Qzk1NS4wNyAyMDEuNzQzIDk1MS43MyAyMDAuNzU1IDk0Ny44MyAyMDAuNzU1Qzk0My44OCAyMDAuNzU1IDk0MC4zNSAyMDEuNjkyIDkzNy4yNiAyMDMuNTY3QzkzNC4yMiAyMDUuNDQyIDkzMS44NCAyMDguMDUxIDkzMC4xMiAyMTEuMzk1QzkyOC40IDIxNC43MzkgOTI3LjU0IDIxOC42NCA5MjcuNTQgMjIzLjA5OUM5MjcuNTQgMjI3LjUwNyA5MjguNCAyMzEuMzgzIDkzMC4xMiAyMzQuNzI3QzkzMS44NCAyMzguMDcxIDkzNC4yMiAyNDAuNjggOTM3LjI2IDI0Mi41NTVDOTQwLjM1IDI0NC40MyA5NDMuODggMjQ1LjM2NyA5NDcuODMgMjQ1LjM2N0M5NTEuNzMgMjQ1LjM2NyA5NTUuMDcgMjQ0LjQwNCA5NTcuODYgMjQyLjQ3OUM5NjAuNjUgMjQwLjUwMyA5NjIuNyAyMzcuOTQ0IDk2NC4wMiAyMzQuODAzTDk3MC44NiAyMzcuOTE5Qzk2OS45NCAyNDAuNDAyIDk2OC40IDI0Mi43MzIgOTY2LjIyIDI0NC45MTFDOTY0LjA5IDI0Ny4wOSA5NjEuNDYgMjQ4Ljg2MyA5NTguMzIgMjUwLjIzMUM5NTUuMjIgMjUxLjU5OSA5NTEuNzMgMjUyLjI4MyA5NDcuODMgMjUyLjI4M1pNMTAwMS4xNCAyNTIuMjgzQzk5Ny4xOSAyNTIuMjgzIDk5My42MiAyNTEuMzcxIDk5MC40MyAyNDkuNTQ3Qzk4Ny4yNCAyNDcuNjcyIDk4NC43IDI0NS4xMTQgOTgyLjgzIDI0MS44NzFDOTgwLjk1IDIzOC42MjggOTgwLjAyIDIzNC45NTUgOTgwLjAyIDIzMC44NTFDOTgwLjAyIDIyNi43NDcgOTgwLjkzIDIyMy4wOTkgOTgyLjc1IDIxOS45MDdDOTg0LjYzIDIxNi43MTUgOTg3LjE2IDIxNC4xODIgOTkwLjM1IDIxMi4zMDdDOTkzLjU0IDIxMC40MzIgOTk3LjE0IDIwOS40OTUgMTAwMS4xNCAyMDkuNDk1QzEwMDUuMSAyMDkuNDk1IDEwMDguNjcgMjEwLjQzMiAxMDExLjg2IDIxMi4zMDdDMTAxNS4wNSAyMTQuMTMxIDEwMTcuNTYgMjE2LjYzOSAxMDE5LjM4IDIxOS44MzFDMTAyMS4yNiAyMjMuMDIzIDEwMjIuMiAyMjYuNjk2IDEwMjIuMiAyMzAuODUxQzEwMjIuMiAyMzUuMDA2IDEwMjEuMjMgMjM4LjcwNCAxMDE5LjMxIDI0MS45NDdDMTAxNy4zOCAyNDUuMTM5IDEwMTQuODIgMjQ3LjY3MiAxMDExLjYzIDI0OS41NDdDMTAwOC40OSAyNTEuMzcxIDEwMDQuOTkgMjUyLjI4MyAxMDAxLjE0IDI1Mi4yODNaTTEwMDEuMTQgMjQ1LjQ0M0MxMDAzLjY4IDI0NS40NDMgMTAwNS45NiAyNDQuODEgMTAwNy45OCAyNDMuNTQzQzEwMTAuMDYgMjQyLjI3NiAxMDExLjY4IDI0MC41MjggMTAxMi44NSAyMzguMjk5QzEwMTQuMDYgMjM2LjA3IDEwMTQuNjcgMjMzLjU4NyAxMDE0LjY3IDIzMC44NTFDMTAxNC42NyAyMjguMDY0IDEwMTQuMDYgMjI1LjYwNyAxMDEyLjg1IDIyMy40NzlDMTAxMS42OCAyMjEuMyAxMDEwLjA2IDIxOS41NzggMTAwNy45OCAyMTguMzExQzEwMDUuOTYgMjE2Ljk5NCAxMDAzLjY4IDIxNi4zMzUgMTAwMS4xNCAyMTYuMzM1Qzk5OC41NiAyMTYuMzM1IDk5Ni4yMyAyMTYuOTk0IDk5NC4xNSAyMTguMzExQzk5Mi4xMyAyMTkuNTc4IDk5MC41IDIyMS4zIDk4OS4yOSAyMjMuNDc5Qzk4OC4wNyAyMjUuNjA3IDk4Ny40NiAyMjguMDY0IDk4Ny40NiAyMzAuODUxQzk4Ny40NiAyMzMuNTg3IDk4OC4wNyAyMzYuMDcgOTg5LjI5IDIzOC4yOTlDOTkwLjUgMjQwLjUyOCA5OTIuMTMgMjQyLjI3NiA5OTQuMTUgMjQzLjU0M0M5OTYuMjMgMjQ0LjgxIDk5OC41NiAyNDUuNDQzIDEwMDEuMTQgMjQ1LjQ0M1pNMTAzMy42OSAyNTEuMzcxVjIxMC40MDdIMTA0MC42MVYyMTcuOTMxTDEwMzkuODUgMjE2Ljg2N0MxMDQwLjgxIDIxNC41MzYgMTA0Mi4yOCAyMTIuODE0IDEwNDQuMjYgMjExLjY5OUMxMDQ2LjIzIDIxMC41MzQgMTA0OC42NCAyMDkuOTUxIDEwNTEuNDggMjA5Ljk1MUgxMDUzLjk5VjIxNi42MzlIMTA1MC40MUMxMDQ3LjUzIDIxNi42MzkgMTA0NS4yIDIxNy41NTEgMTA0My40MiAyMTkuMzc1QzEwNDEuNjUgMjIxLjE0OCAxMDQwLjc2IDIyMy42ODIgMTA0MC43NiAyMjYuOTc1VjI1MS4zNzFIMTAzMy42OVpNMTA4MS4zOSAyNTIuMjgzQzEwNzcuNDQgMjUyLjI4MyAxMDczLjkyIDI1MS4zNDYgMTA3MC44MyAyNDkuNDcxQzEwNjcuNzQgMjQ3LjU5NiAxMDY1LjMxIDI0NS4wMzggMTA2My41MyAyNDEuNzk1QzEwNjEuNzYgMjM4LjUwMiAxMDYwLjg3IDIzNC44MjggMTA2MC44NyAyMzAuNzc1QzEwNjAuODcgMjI2LjY3MSAxMDYxLjczIDIyMy4wMjMgMTA2My40NiAyMTkuODMxQzEwNjUuMjMgMjE2LjYzOSAxMDY3LjYxIDIxNC4xMzEgMTA3MC42IDIxMi4zMDdDMTA3My42NCAyMTAuNDMyIDEwNzcuMDQgMjA5LjQ5NSAxMDgwLjc4IDIwOS40OTVDMTA4My44MiAyMDkuNDk1IDEwODYuNTEgMjEwLjA1MiAxMDg4Ljg0IDIxMS4xNjdDMTA5MS4yMiAyMTIuMjMxIDEwOTMuMjIgMjEzLjcgMTA5NC44NCAyMTUuNTc1QzEwOTYuNTIgMjE3LjM5OSAxMDk3Ljc4IDIxOS41MDIgMTA5OC42NCAyMjEuODgzQzEwOTkuNTYgMjI0LjIxNCAxMTAwLjAxIDIyNi42NDYgMTEwMC4wMSAyMjkuMTc5QzExMDAuMDEgMjI5LjczNiAxMDk5Ljk2IDIzMC4zNyAxMDk5Ljg2IDIzMS4wNzlDMTA5OS44MSAyMzEuNzM4IDEwOTkuNzMgMjMyLjM3MSAxMDk5LjYzIDIzMi45NzlIMTA2Ni4wNFYyMjYuODk5SDEwOTUuNTNMMTA5Mi4xOCAyMjkuNjM1QzEwOTIuNjQgMjI3IDEwOTIuMzkgMjI0LjY0NCAxMDkxLjQyIDIyMi41NjdDMTA5MC40NiAyMjAuNDkgMTA4OS4wNCAyMTguODQzIDEwODcuMTcgMjE3LjYyN0MxMDg1LjI5IDIxNi40MTEgMTA4My4xNyAyMTUuODAzIDEwODAuNzggMjE1LjgwM0MxMDc4LjQgMjE1LjgwMyAxMDc2LjIyIDIxNi40MTEgMTA3NC4yNSAyMTcuNjI3QzEwNzIuMjcgMjE4Ljg0MyAxMDcwLjczIDIyMC41OTEgMTA2OS42MSAyMjIuODcxQzEwNjguNTUgMjI1LjEgMTA2OC4xMiAyMjcuNzYgMTA2OC4zMiAyMzAuODUxQzEwNjguMTIgMjMzLjg0IDEwNjguNTcgMjM2LjQ3NSAxMDY5LjY5IDIzOC43NTVDMTA3MC44NSAyNDAuOTg0IDEwNzIuNDggMjQyLjczMiAxMDc0LjU1IDI0My45OTlDMTA3Ni42OCAyNDUuMjE1IDEwNzguOTkgMjQ1LjgyMyAxMDgxLjQ3IDI0NS44MjNDMTA4NC4yIDI0NS44MjMgMTA4Ni41MSAyNDUuMTkgMTA4OC4zOCAyNDMuOTIzQzEwOTAuMjYgMjQyLjY1NiAxMDkxLjc4IDI0MS4wMzUgMTA5Mi45NCAyMzkuMDU5TDEwOTguODcgMjQyLjA5OUMxMDk4LjA2IDI0My45NzQgMTA5Ni44IDI0NS42OTYgMTA5NS4wNyAyNDcuMjY3QzEwOTMuNCAyNDguNzg3IDEwOTEuNCAyNTAuMDAzIDEwODkuMDcgMjUwLjkxNUMxMDg2Ljc5IDI1MS44MjcgMTA4NC4yMyAyNTIuMjgzIDEwODEuMzkgMjUyLjI4M1pNMTEyMi43NiAyNTEuMzcxTDExMDYuODcgMTk0Ljc1MUgxMTE0LjdMMTEyOCAyNDQuNjA3SDExMjYuMThMMTE0MC4wMSAxOTQuNzUxSDExNDcuODRMMTE2MS41OSAyNDQuNjA3SDExNTkuNjlMMTE3My4wNyAxOTQuNzUxSDExODAuOUwxMTY1LjAxIDI1MS4zNzFIMTE1Ni43M0wxMTQyLjkgMjAxLjc0M0gxMTQ0Ljg3TDExMzEuMDQgMjUxLjM3MUgxMTIyLjc2Wk0xMjA1LjUyIDI1Mi4yODNDMTIwMS41NyAyNTIuMjgzIDExOTguMDUgMjUxLjM0NiAxMTk0Ljk2IDI0OS40NzFDMTE5MS44NiAyNDcuNTk2IDExODkuNDMgMjQ1LjAzOCAxMTg3LjY2IDI0MS43OTVDMTE4NS44OSAyMzguNTAyIDExODUgMjM0LjgyOCAxMTg1IDIzMC43NzVDMTE4NSAyMjYuNjcxIDExODUuODYgMjIzLjAyMyAxMTg3LjU4IDIxOS44MzFDMTE4OS4zNiAyMTYuNjM5IDExOTEuNzQgMjE0LjEzMSAxMTk0LjczIDIxMi4zMDdDMTE5Ny43NyAyMTAuNDMyIDEyMDEuMTYgMjA5LjQ5NSAxMjA0LjkxIDIwOS40OTVDMTIwNy45NSAyMDkuNDk1IDEyMTAuNjQgMjEwLjA1MiAxMjEyLjk3IDIxMS4xNjdDMTIxNS4zNSAyMTIuMjMxIDEyMTcuMzUgMjEzLjcgMTIxOC45NyAyMTUuNTc1QzEyMjAuNjQgMjE3LjM5OSAxMjIxLjkxIDIxOS41MDIgMTIyMi43NyAyMjEuODgzQzEyMjMuNjggMjI0LjIxNCAxMjI0LjE0IDIyNi42NDYgMTIyNC4xNCAyMjkuMTc5QzEyMjQuMTQgMjI5LjczNiAxMjI0LjA5IDIzMC4zNyAxMjIzLjk5IDIzMS4wNzlDMTIyMy45NCAyMzEuNzM4IDEyMjMuODYgMjMyLjM3MSAxMjIzLjc2IDIzMi45NzlIMTE5MC4xN1YyMjYuODk5SDEyMTkuNjZMMTIxNi4zMSAyMjkuNjM1QzEyMTYuNzcgMjI3IDEyMTYuNTEgMjI0LjY0NCAxMjE1LjU1IDIyMi41NjdDMTIxNC41OSAyMjAuNDkgMTIxMy4xNyAyMTguODQzIDEyMTEuMyAyMTcuNjI3QzEyMDkuNDIgMjE2LjQxMSAxMjA3LjI5IDIxNS44MDMgMTIwNC45MSAyMTUuODAzQzEyMDIuNTMgMjE1LjgwMyAxMjAwLjM1IDIxNi40MTEgMTE5OC4zOCAyMTcuNjI3QzExOTYuNCAyMTguODQzIDExOTQuODUgMjIwLjU5MSAxMTkzLjc0IDIyMi44NzFDMTE5Mi42OCAyMjUuMSAxMTkyLjI0IDIyNy43NiAxMTkyLjQ1IDIzMC44NTFDMTE5Mi4yNCAyMzMuODQgMTE5Mi43IDIzNi40NzUgMTE5My44MiAyMzguNzU1QzExOTQuOTggMjQwLjk4NCAxMTk2LjYgMjQyLjczMiAxMTk4LjY4IDI0My45OTlDMTIwMC44MSAyNDUuMjE1IDEyMDMuMTEgMjQ1LjgyMyAxMjA1LjYgMjQ1LjgyM0MxMjA4LjMzIDI0NS44MjMgMTIxMC42NCAyNDUuMTkgMTIxMi41MSAyNDMuOTIzQzEyMTQuMzkgMjQyLjY1NiAxMjE1LjkxIDI0MS4wMzUgMTIxNy4wNyAyMzkuMDU5TDEyMjMgMjQyLjA5OUMxMjIyLjE5IDI0My45NzQgMTIyMC45MiAyNDUuNjk2IDEyMTkuMiAyNDcuMjY3QzEyMTcuNTMgMjQ4Ljc4NyAxMjE1LjUzIDI1MC4wMDMgMTIxMy4yIDI1MC45MTVDMTIxMC45MiAyNTEuODI3IDEyMDguMzYgMjUyLjI4MyAxMjA1LjUyIDI1Mi4yODNaTTEyNDcuMTIgMjUyLjI4M0MxMjQ0LjQ0IDI1Mi4yODMgMTI0Mi4wNiAyNTEuODAyIDEyMzkuOTggMjUwLjgzOUMxMjM3Ljk1IDI0OS44MjYgMTIzNi4zNiAyNDguNDU4IDEyMzUuMTkgMjQ2LjczNUMxMjM0LjAzIDI0NC45NjIgMTIzMy40NCAyNDIuOTM1IDEyMzMuNDQgMjQwLjY1NUMxMjMzLjQ0IDIzOC40NzYgMTIzMy45IDIzNi41MjYgMTIzNC44MSAyMzQuODAzQzEyMzUuNzcgMjMzLjAzIDEyMzcuMjQgMjMxLjUzNSAxMjM5LjIyIDIzMC4zMTlDMTI0MS4yNSAyMjkuMTAzIDEyNDMuNzggMjI4LjI0MiAxMjQ2LjgyIDIyNy43MzVMMTI2Mi4wMiAyMjUuMjI3VjIzMS4xNTVMMTI0OC40MiAyMzMuNDM1QzEyNDUuNzggMjMzLjg5MSAxMjQzLjg2IDIzNC43MjcgMTI0Mi42NCAyMzUuOTQzQzEyNDEuNDcgMjM3LjE1OSAxMjQwLjg5IDIzOC42NTQgMTI0MC44OSAyNDAuNDI3QzEyNDAuODkgMjQyLjA5OSAxMjQxLjU1IDI0My40OTIgMTI0Mi44NyAyNDQuNjA3QzEyNDQuMjQgMjQ1LjcyMiAxMjQ1LjkzIDI0Ni4yNzkgMTI0Ny45NiAyNDYuMjc5QzEyNTAuNTQgMjQ2LjI3OSAxMjUyLjc3IDI0NS43NDcgMTI1NC42NSAyNDQuNjgzQzEyNTYuNTcgMjQzLjU2OCAxMjU4LjA3IDI0Mi4wNzQgMTI1OS4xMyAyNDAuMTk5QzEyNjAuMjUgMjM4LjMyNCAxMjYwLjggMjM2LjI0NyAxMjYwLjggMjMzLjk2N1YyMjMuNTU1QzEyNjAuOCAyMjEuMzI2IDEyNTkuOTcgMjE5LjUyNyAxMjU4LjMgMjE4LjE1OUMxMjU2LjY3IDIxNi43NCAxMjU0LjUyIDIxNi4wMzEgMTI1MS44NCAyMTYuMDMxQzEyNDkuNSAyMTYuMDMxIDEyNDcuNDMgMjE2LjYzOSAxMjQ1LjYgMjE3Ljg1NUMxMjQzLjgzIDIxOS4wMiAxMjQyLjUxIDIyMC41OTEgMTI0MS42NSAyMjIuNTY3TDEyMzUuNSAyMTkuMzc1QzEyMzYuMjYgMjE3LjUgMTIzNy40NyAyMTUuODI4IDEyMzkuMTQgMjE0LjM1OUMxMjQwLjgyIDIxMi44MzkgMTI0Mi43NyAyMTEuNjQ4IDEyNDUgMjEwLjc4N0MxMjQ3LjIyIDIwOS45MjYgMTI0OS41NiAyMDkuNDk1IDEyNTEuOTkgMjA5LjQ5NUMxMjU1LjEzIDIwOS40OTUgMTI1Ny44OSAyMTAuMTAzIDEyNjAuMjcgMjExLjMxOUMxMjYyLjY1IDIxMi40ODQgMTI2NC41IDIxNC4xMzEgMTI2NS44MiAyMTYuMjU5QzEyNjcuMTkgMjE4LjMzNiAxMjY3Ljg3IDIyMC43NjggMTI2Ny44NyAyMjMuNTU1VjI1MS4zNzFIMTI2MC45NlYyNDMuNjE5TDEyNjIuMjUgMjQ0LjA3NUMxMjYxLjM5IDI0NS42OTYgMTI2MC4yMiAyNDcuMTE1IDEyNTguNzUgMjQ4LjMzMUMxMjU3LjI4IDI0OS41NDcgMTI1NS41NiAyNTAuNTEgMTI1My41OCAyNTEuMjE5QzEyNTEuNjEgMjUxLjkyOCAxMjQ5LjQ1IDI1Mi4yODMgMTI0Ny4xMiAyNTIuMjgzWk0xMjkxLjc3IDI1MS4zNzFMMTI3NS43MyAyMTAuNDA3SDEyODMuNjRMMTI5Ni40OCAyNDUuMDYzSDEyOTMuNzRMMTMwNi42NiAyMTAuNDA3SDEzMTQuNTdMMTI5OC40NiAyNTEuMzcxSDEyOTEuNzdaTTEzNDEuMjggMjUyLjI4M0MxMzM3LjMzIDI1Mi4yODMgMTMzMy44IDI1MS4zNDYgMTMzMC43MSAyNDkuNDcxQzEzMjcuNjIgMjQ3LjU5NiAxMzI1LjE5IDI0NS4wMzggMTMyMy40MiAyNDEuNzk1QzEzMjEuNjQgMjM4LjUwMiAxMzIwLjc2IDIzNC44MjggMTMyMC43NiAyMzAuNzc1QzEzMjAuNzYgMjI2LjY3MSAxMzIxLjYyIDIyMy4wMjMgMTMyMy4zNCAyMTkuODMxQzEzMjUuMTEgMjE2LjYzOSAxMzI3LjUgMjE0LjEzMSAxMzMwLjQ5IDIxMi4zMDdDMTMzMy41MyAyMTAuNDMyIDEzMzYuOTIgMjA5LjQ5NSAxMzQwLjY3IDIwOS40OTVDMTM0My43MSAyMDkuNDk1IDEzNDYuMzkgMjEwLjA1MiAxMzQ4LjczIDIxMS4xNjdDMTM1MS4xMSAyMTIuMjMxIDEzNTMuMTEgMjEzLjcgMTM1NC43MyAyMTUuNTc1QzEzNTYuNCAyMTcuMzk5IDEzNTcuNjcgMjE5LjUwMiAxMzU4LjUzIDIyMS44ODNDMTM1OS40NCAyMjQuMjE0IDEzNTkuOSAyMjYuNjQ2IDEzNTkuOSAyMjkuMTc5QzEzNTkuOSAyMjkuNzM2IDEzNTkuODUgMjMwLjM3IDEzNTkuNzUgMjMxLjA3OUMxMzU5LjY5IDIzMS43MzggMTM1OS42MiAyMzIuMzcxIDEzNTkuNTIgMjMyLjk3OUgxMzI1LjkzVjIyNi44OTlIMTM1NS40MUwxMzUyLjA3IDIyOS42MzVDMTM1Mi41MyAyMjcgMTM1Mi4yNyAyMjQuNjQ0IDEzNTEuMzEgMjIyLjU2N0MxMzUwLjM1IDIyMC40OSAxMzQ4LjkzIDIxOC44NDMgMTM0Ny4wNSAyMTcuNjI3QzEzNDUuMTggMjE2LjQxMSAxMzQzLjA1IDIxNS44MDMgMTM0MC42NyAyMTUuODAzQzEzMzguMjkgMjE1LjgwMyAxMzM2LjExIDIxNi40MTEgMTMzNC4xMyAyMTcuNjI3QzEzMzIuMTYgMjE4Ljg0MyAxMzMwLjYxIDIyMC41OTEgMTMyOS41IDIyMi44NzFDMTMyOC40MyAyMjUuMSAxMzI4IDIyNy43NiAxMzI4LjIxIDIzMC44NTFDMTMyOCAyMzMuODQgMTMyOC40NiAyMzYuNDc1IDEzMjkuNTcgMjM4Ljc1NUMxMzMwLjc0IDI0MC45ODQgMTMzMi4zNiAyNDIuNzMyIDEzMzQuNDQgMjQzLjk5OUMxMzM2LjU3IDI0NS4yMTUgMTMzOC44NyAyNDUuODIzIDEzNDEuMzUgMjQ1LjgyM0MxMzQ0LjA5IDI0NS44MjMgMTM0Ni4zOSAyNDUuMTkgMTM0OC4yNyAyNDMuOTIzQzEzNTAuMTQgMjQyLjY1NiAxMzUxLjY2IDI0MS4wMzUgMTM1Mi44MyAyMzkuMDU5TDEzNTguNzYgMjQyLjA5OUMxMzU3Ljk1IDI0My45NzQgMTM1Ni42OCAyNDUuNjk2IDEzNTQuOTYgMjQ3LjI2N0MxMzUzLjI5IDI0OC43ODcgMTM1MS4yOCAyNTAuMDAzIDEzNDguOTUgMjUwLjkxNUMxMzQ2LjY3IDI1MS44MjcgMTM0NC4xMSAyNTIuMjgzIDEzNDEuMjggMjUyLjI4M1oiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMTA1Mi4xOCA0MS4zMTZDMTA1NS4zNyA0MS4zMTYgMTA1OC4xNyA0MC4zMjIgMTA2MC4xNiAzOC4zMzRDMTA2Mi4zNiAzNi4zNDYgMTA2My41NSAzMy43NjEgMTA2My41NSAzMC41OEMxMDYzLjU1IDI3LjM5OSAxMDYyLjM2IDI0LjgxNCAxMDYwLjE2IDIyLjgyNkMxMDU3Ljk3IDIwLjgzOCAxMDU1LjM3IDE5Ljg0NCAxMDUyLjE4IDE5Ljg0NEMxMDQ4Ljk4IDE5Ljg0NCAxMDQ2LjE5IDIwLjgzOCAxMDQzLjk5IDIyLjgyNkMxMDQxLjc5IDI0LjgxNCAxMDQwLjU5IDI3LjM5OSAxMDQwLjU5IDMwLjU4QzEwNDAuNTkgMzMuNzYxIDEwNDEuNzkgMzYuMzQ2IDEwNDMuOTkgMzguMzM0QzEwNDYuMTkgNDAuMzIyIDEwNDguOTggNDEuMzE2IDEwNTIuMTggNDEuMzE2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik00MzcuMzc2IDg2LjI1MkM0MzcuMzc2IDgwLjA4OCA0MzYuMTc4IDc0LjcyIDQzMy41ODMgNzAuMzQ2QzQzMS4xODcgNjUuNzczIDQyNy43OTIgNjIuMzkzIDQyMy40MDIgNTkuODA5QzQxOS4wMDggNTcuMjI0IDQxMy44MTUgNTYuMDMxIDQwNy44MjUgNTYuMDMxQzQwMS40MzcgNTYuMDMxIDM5NS40NDcgNTcuNjIyIDM4OS44NTUgNjAuNjA0QzM4NC4yNjQgNjMuNTg2IDM3OS42NzEgNjcuOTYgMzc2LjI4IDczLjkyNUMzNzIuODg1IDc5LjY5MSAzNzEuMDg2IDg2LjQ1MSAzNzEuMDg2IDk0LjYwMkMzNzEuMDg2IDEwMi43NTMgMzcyLjY4NiAxMDkuMTE2IDM3NS42NzkgMTE0Ljg4MUMzNzguNjc2IDEyMC40NDggMzgyLjg2NyAxMjQuODIyIDM4OC4yNTkgMTI3LjgwNUMzOTMuNjQ4IDEzMC43ODcgMzk5Ljg0MSAxMzIuMzc3IDQwNi44MjYgMTMyLjM3N0M0MTMuODE1IDEzMi4zNzcgNDIwLjAwNyAxMzAuNzg3IDQyNC45OTggMTI3LjgwNUM0MzAuMTg4IDEyNC42MjMgNDM0LjE4NCAxMjAuNDQ4IDQzNy4xNzcgMTE0Ljg4MUw0MzIuNzgzIDExMC45MDVDNDMwLjE4OCAxMTMuNjg4IDQyNy4zOTQgMTE2LjA3NSA0MjQuMzk3IDExNy44NjRDNDIxLjQwNCAxMTkuNjUzIDQxNy42MTEgMTIwLjQ0OCA0MTMuMjE4IDEyMC40NDhDNDA2LjgyNiAxMjAuNDQ4IDQwMS42MzYgMTE4LjI2MSAzOTcuMjQyIDExMy44ODdDMzkzLjA1MSAxMDkuNTEzIDM5MC44NTQgMTAzLjE1MSAzOTAuNDU2IDk0LjQwM0g0MzYuNzc5QzQzNi45NzggOTIuMjE2IDQzNy4zNzYgODkuNDMzIDQzNy4zNzYgODYuMjUyWk00MTguNDA4IDg1LjI1N0M0MTcuMjEgODYuODQ4IDQxNC44MTQgODcuNDQ1IDQxMS4yMiA4Ny40NDVIMzkwLjQ1NkMzOTAuODU0IDgxLjQ4IDM5MS44NTMgNzYuNzA4IDM5My40NDkgNzMuMTI5QzM5NS4yNDggNjkuNTUxIDM5Ny4yNDIgNjcuMTY1IDM5OS40MzkgNjUuNTc0QzQwMS44MzUgNjMuOTg0IDQwNC4yMzEgNjMuMTg5IDQwNi42MjcgNjMuMTg5QzQxMC40MjQgNjMuMTg5IDQxMy42MTYgNjQuNTgxIDQxNi4yMTEgNjcuNTYzQzQxOC44MDkgNzAuNTQ1IDQyMC4yMDYgNzQuMzIyIDQyMC4yMDYgNzguODk1QzQyMC4wMDcgODEuNDggNDE5LjQwNyA4My42NjcgNDE4LjQwOCA4NS4yNTdaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTU0Ny44MSA2Mi4yMDFDNTQyLjYxNyA1OC4wMjUgNTM1LjQyOSA1NS44MzkgNTI2LjI0NyA1NS44MzlDNTE3LjA2MSA1NS44MzkgNTA5Ljg3MyA1OC4wMjUgNTA0LjY4IDYyLjU5OEM0OTkuNDkgNjYuOTcyIDQ5Ni44OTUgNzIuOTM3IDQ5Ni44OTUgODAuMjkzQzQ5Ni44OTUgOTAuMDM1IDUwMC44ODcgOTYuOTk0IDUwOC44NzUgMTAwLjk3QzUwNS4wODIgMTA0LjM1IDUwMi4yODQgMTA3LjUzMSA1MDAuNDg5IDExMC41MTRDNDk4LjY5IDExMy4yOTcgNDk3Ljg5NCAxMTYuMjc5IDQ5Ny44OTQgMTE5LjA2M0M0OTcuODk0IDEyMS44NDYgNDk4LjY5IDEyNC4yMzIgNTAwLjA4NyAxMjYuMjJDNTAxLjY4NyAxMjguMjA4IDUwMy44ODQgMTI5Ljc5OSA1MDcuMDc2IDEzMC43OTNDNTAyLjI4NCAxMzMuMTc5IDQ5OC42OSAxMzUuNTY1IDQ5Ni42OTYgMTM4LjE0OUM0OTQuNDk5IDE0MC45MzMgNDkzLjUgMTQzLjkxNSA0OTMuNSAxNDcuMDk2QzQ5My41IDE1MC4yNzcgNDk0LjQ5OSAxNTMuNDU4IDQ5Ni40OTMgMTU2LjA0M0M0OTguNjkgMTU4LjgyNyA1MDIuMDg1IDE2MC44MTQgNTA2LjY3OCAxNjIuNjA0QzUxMS40NyAxNjQuMTk0IDUxNy42NTggMTY0Ljk5IDUyNS40NDcgMTY0Ljk5QzUzNC40MzQgMTY0Ljk5IDU0MS44MjEgMTYzLjc5NyA1NDcuODEgMTYxLjIxMkM1NTMuOCAxNTguNjI4IDU1OC4zOTMgMTU1LjQ0NyA1NjEuMzg2IDE1MS4yNzFDNTY0LjU4MiAxNDcuMDk2IDU2NS45NzkgMTQyLjcyMiA1NjUuOTc5IDEzNy45NUM1NjUuOTc5IDEzMS41ODggNTYzLjc4MiAxMjYuNjE4IDU1OS41OTEgMTIyLjg0QzU1NS4zOTYgMTE5LjA2MyA1NDguNDA4IDExNy4yNzMgNTM4LjQyNiAxMTcuMjczSDUxOS40NTdDNTE2LjA2MiAxMTcuMjczIDUxMy44NjUgMTE2LjY3NyA1MTIuNDY4IDExNS42ODNDNTExLjI3IDExNC40OSA1MTAuNjcgMTEzLjA5OCA1MTAuNjcgMTExLjExQzUxMC42NyAxMDguMTI4IDUxMS42NjkgMTA1LjM0NCA1MTMuNDY3IDEwMi43NkM1MTcuMjYgMTAzLjk1MyA1MjEuNDU1IDEwNC4zNSA1MjYuMDQ0IDEwNC4zNUM1MzUuMjMgMTA0LjM1IDU0Mi42MTcgMTAyLjE2MyA1NDcuNjExIDk3Ljc4OUM1NTIuODAxIDkzLjIxNyA1NTUuMzk2IDg3LjI1MiA1NTUuMzk2IDgwLjA5NEM1NTUuMzk2IDc1LjEyNCA1NTQuMzk3IDcwLjk0OSA1NTIuMjA0IDY3LjM3SDU2Ni43NzlWNTYuODMzTDU2NC41ODIgNTUuMjQyTDU0Ny44MSA2Mi4yMDFaTTUxMS4wNzEgMTMyLjc4MUM1MTQuMDY1IDEzMy4zNzggNTE3LjI2IDEzMy43NzUgNTIxLjA1MyAxMzMuNzc1SDUzNy44MjVDNTQyLjYxNyAxMzMuNzc1IDU0Ni4wMTIgMTM0Ljc2OSA1NDguMDA5IDEzNi43NThDNTUwLjAwNyAxMzguNzQ2IDU1MS4wMDYgMTQxLjEzMiA1NTEuMDA2IDE0My45MTVDNTUxLjAwNiAxNDcuNjkzIDU0OS4wMDggMTUwLjg3NCA1NDQuODE0IDE1My40NThDNTQwLjgyMiAxNTYuMDQzIDUzNC44MzIgMTU3LjQzNSA1MjYuODQ0IDE1Ny40MzVDNTIwLjQ1NiAxNTcuNDM1IDUxNS42NjQgMTU2LjQ0MSA1MTIuMjY5IDE1NC4yNTRDNTA4Ljg3NSAxNTIuMDY3IDUwNy4wNzYgMTQ4LjY4NyA1MDcuMDc2IDE0NC4xMTRDNTA2Ljg3NyAxNDAuMzM2IDUwOC4yNzQgMTM2LjU1OSA1MTEuMDcxIDEzMi43ODFaTTUzNS42MzIgOTMuMjE3QzUzMy40MzUgOTYuNTk2IDUzMC4yMzkgOTguMTg3IDUyNi4wNDQgOTguMTg3QzUyMS44NTMgOTguMTg3IDUxOC44NTYgOTYuNTk2IDUxNi44NjIgOTMuNDE1QzUxNC42NjUgOTAuMjM0IDUxMy42NjYgODUuODYgNTEzLjY2NiA4MC40OTJDNTEzLjY2NiA3NS4xMjQgNTE0Ljg2NCA3MC43NSA1MTcuMDYxIDY3LjU2OUM1MTkuNDU3IDY0LjE4OSA1MjIuNjUzIDYyLjU5OCA1MjYuNjQ1IDYyLjU5OEM1MzAuNjM3IDYyLjU5OCA1MzMuODMzIDY0LjE4OSA1MzUuODMxIDY3LjM3QzUzOC4wMjggNzAuNTUxIDUzOS4yMjYgNzQuNzI2IDUzOS4yMjYgODAuMDk0QzUzOS4wMjMgODUuNDYzIDUzOC4wMjggOTAuMDM1IDUzNS42MzIgOTMuMjE3WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik02NDcuNjI1IDExMC4xMDNWODIuODY1QzY0Ny42MjUgNzMuNTIgNjQ1LjgzIDY2Ljc2IDY0Mi4yMzYgNjIuMzg3QzYzOC42NDIgNTguMDEzIDYzMy40NDggNTUuODI1IDYyNy4wNiA1NS44MjVDNjE3LjY3NiA1NS44MjUgNjA4Ljg5MiA2MC4yIDYwMS4zMDIgNjkuMTQ3VjQyLjMwNkw2MDEuOTAzIDIxLjAzMkw1OTkuNzA2IDE5LjY0MUw1NzIuNzUgMjYuNFYzMi4zNjVMNTgzLjczMSAzMy45NTZWMTA5LjkwNEM1ODMuNzMxIDExNC4yNzggNTgzLjczMSAxMTguMjU0IDU4My41MzIgMTIyLjAzMkw1NzMuNTUgMTI0LjAyVjEzMC4xODRINjEwLjg4NlYxMjQuMDJMNjAxLjkwMyAxMjIuMjMxQzYwMS43IDExOC40NTMgNjAxLjcgMTE0LjI3OCA2MDEuNyAxMTAuMTAzVjc3LjI5OEM2MDcuNjk0IDcxLjUzMiA2MTMuNjg0IDY4Ljc0OSA2MTkuMjcyIDY4Ljc0OUM2MjMuMDY4IDY4Ljc0OSA2MjUuODYyIDY5Ljk0MiA2MjcuMjYgNzIuMTI5QzYyOC44NTYgNzQuMzE2IDYyOS42NTUgNzguNDkxIDYyOS42NTUgODQuMjU3VjExMC4xMDNDNjI5LjY1NSAxMTQuMjc4IDYyOS42NTUgMTE4LjI1NCA2MjkuNDU2IDEyMi4wMzJMNjE5Ljg3MyAxMjQuMDJWMTMwLjE4NEg2NTcuMDFWMTI0LjAyTDY0Ny44MjggMTIyLjIzMUM2NDcuNjI1IDExOC40NTMgNjQ3LjYyNSAxMTQuNDc3IDY0Ny42MjUgMTEwLjEwM1oiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMzc2LjI5NyAzMC4zODNIMzQyLjk1MVYzNy4zNDJMMzU1LjMzIDM5LjEzMUwzMzYuOTYxIDEwNC45NEwzMTYuNzk0IDM4LjkzMkwzMzAuOTcxIDM3LjM0MlYzMC4zODNIMjg3Ljg0MlYzNy4zNDJMMzAxLjAyIDM4LjkzMkwyODAuMjU0IDEwNC4xNDVMMjYzLjA4MiAzOC45MzJMMjc1LjY2MiAzNy4zNDJWMzAuMzgzSDIzMS43MzRWMzcuMzQyTDI0Mi43MTYgMzguNTM0TDI2OS44NzEgMTMwLjU4N0gyODAuMjU0TDMwMy4wMTcgNTcuMjIzTDMyNi45NzcgMTMwLjU4N0gzMzcuMzZMMzYzLjUxNyAzOS4xMzFMMzc1LjY5NiAzNy4xNDNWMzAuMzgzSDM3Ni4yOTdaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTQ2Ny4xMjggNDEuOTE4QzQ3MC4zMjEgNDEuOTE4IDQ3My4xMTggNDAuOTI0IDQ3NS4xMTIgMzguOTM1QzQ3Ny4zMDkgMzYuOTQ3IDQ3OC41MDcgMzQuMzYzIDQ3OC41MDcgMzEuMTgyQzQ3OC41MDcgMjggNDc3LjMwOSAyNS40MTYgNDc1LjExMiAyMy40MjhDNDcyLjkxNiAyMS40MzkgNDcwLjMyMSAyMC40NDUgNDY3LjEyOCAyMC40NDVDNDYzLjkzMyAyMC40NDUgNDYxLjEzNSAyMS40MzkgNDU4Ljk0MiAyMy40MjhDNDU2Ljc0NSAyNS40MTYgNDU1LjU0NyAyOCA0NTUuNTQ3IDMxLjE4MkM0NTUuNTQ3IDM0LjM2MyA0NTYuNzQ1IDM2Ljk0NyA0NTguOTQyIDM4LjkzNUM0NjEuMTM1IDQwLjkyNCA0NjMuOTMzIDQxLjkxOCA0NjcuMTI4IDQxLjkxOFoiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNNDc2LjExNCAxMDkuOTA2Vjc4LjQ5M0w0NzYuNTEyIDU3LjIyTDQ3NC4xMTYgNTUuNjI5TDQ0Ni45NjEgNjUuMTcyVjcwLjkzOEw0NTcuNzQ2IDcyLjMzQzQ1Ny45NDUgNzUuMzEyIDQ1OC4xNDQgNzguMjk0IDQ1OC4xNDQgODEuMDc4QzQ1OC4zNDMgODMuODYxIDQ1OC4zNDMgODcuMjQxIDQ1OC4zNDMgOTEuMjE4VjEwOS43MDhDNDU4LjM0MyAxMTQuMDgyIDQ1OC4zNDMgMTE4LjA1OCA0NTguMTQ0IDEyMS44MzZMNDQ4LjE1OSAxMjMuODI0VjEyOS45ODdINDg1LjY5OFYxMjMuODI0TDQ3Ni41MTIgMTIyLjAzNEM0NzYuMzEzIDExOC4yNTcgNDc2LjExNCAxMTQuMjggNDc2LjExNCAxMDkuOTA2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xMTQ0LjIzIDEyMi4yNDRDMTE0MS4yMyAxMjIuMjQ0IDExMzkuODMgMTIwLjA1NyAxMTM5LjgzIDExNS40ODRWODIuNjhDMTEzOS44MyA3Mi45MzggMTEzNy44MyA2NS43OCAxMTMzLjg0IDYxLjgwNEMxMTI5Ljg1IDU3LjYyOSAxMTIzLjQ2IDU1LjQ0MSAxMTE0LjY4IDU1LjQ0MUMxMTA1Ljg5IDU1LjQ0MSAxMDk4LjEgNTcuMjMxIDEwOTIuNTEgNjAuODFDMTA4Ni45MiA2NC4zODggMTA4My43MyA2OS4xNiAxMDgyLjkzIDc1LjMyM0MxMDgzLjczIDc5Ljg5NiAxMDg2LjUyIDgyLjA4MyAxMDkxLjMxIDgyLjA4M0MxMDkzLjkxIDgyLjA4MyAxMDk1LjkxIDgxLjI4OCAxMDk3LjcgNzkuNDk5QzEwOTkuNSA3Ny43MDkgMTEwMC41IDc1LjEyNCAxMTAwLjkgNzEuNTQ2TDExMDIuNyA2My4xOTVDMTEwMy44OSA2Mi45OTYgMTEwNC44OSA2Mi43OTggMTEwNS44OSA2Mi43OThDMTEwNy4wOSA2Mi41OTkgMTEwOC4wOCA2Mi41OTkgMTEwOC44OCA2Mi41OTlDMTExMy44OCA2Mi41OTkgMTExNy4yNyA2My43OTIgMTExOS4wNyA2Ni4zNzZDMTEyMS4wNiA2OC43NjIgMTEyMi4wNiA3My41MzQgMTEyMi4wNiA4MC40OTNWODQuNjY4QzExMTkuNDcgODUuNDYzIDExMTYuODcgODYuMDU5IDExMTQuMjcgODYuODU1QzExMTEuNjggODcuNjUgMTEwOS40OCA4OC4yNDYgMTEwNy40OSA4OS4wNDJDMTEwMC4zIDkxLjQyOCAxMDk0LjcxIDkzLjYxNSAxMDkwLjcyIDk2LjE5OUMxMDg2LjkyIDk4LjU4NSAxMDg0LjEzIDEwMS4xNyAxMDgyLjczIDEwMy45NTNDMTA4MS4xMyAxMDYuNzM2IDEwODAuNTMgMTA5LjcxOSAxMDgwLjUzIDExMi45QzEwODAuNTMgMTE5LjA2MyAxMDgyLjUzIDEyMy44MzUgMTA4Ni4zMiAxMjcuMDE2QzEwOTAuMzEgMTMwLjE5NyAxMDk1LjExIDEzMS43ODggMTEwMC43IDEzMS43ODhDMTEwNS40OSAxMzEuNzg4IDExMDkuNDggMTMwLjc5NCAxMTEyLjQ4IDEyOS4wMDRDMTExNS40NyAxMjcuMDE2IDExMTguODcgMTI0LjAzNCAxMTIyLjY2IDEyMC4yNTZDMTEyMy42NiAxMjMuODM1IDExMjUuMjYgMTI2LjYxOCAxMTI3Ljg1IDEyOC42MDZDMTEzMC40NSAxMzAuNTk1IDExMzMuNjQgMTMxLjU4OSAxMTM3LjY0IDEzMS41ODlDMTE0MS4yMyAxMzEuNTg5IDExNDQuMjMgMTMwLjc5NCAxMTQ2LjYyIDEyOS40MDJDMTE0OS4yMiAxMjcuODExIDExNTEuMjIgMTI1LjQyNSAxMTUzLjIxIDEyMi4wNDVMMTE0OS44MiAxMTkuMDYzQzExNDcuODIgMTIxLjA1MSAxMTQ2LjAyIDEyMi4yNDQgMTE0NC4yMyAxMjIuMjQ0Wk0xMTIxLjg2IDExNC40OUMxMTE4LjI3IDExNy4wNzUgMTExNS40NyAxMTguNjY2IDExMTMuODggMTE5LjQ2MUMxMTEyLjA4IDEyMC4yNTYgMTExMC40OCAxMjAuNjU0IDExMDguNjkgMTIwLjY1NEMxMTA1LjY5IDEyMC42NTQgMTEwMy4wOSAxMTkuODU5IDExMDAuOSAxMTguMDY5QzEwOTguOSAxMTYuMjggMTA5Ny45IDExMy4yOTggMTA5Ny45IDEwOS41MkMxMDk3LjkgMTA2LjUzOCAxMDk4LjkgMTAzLjc1NCAxMTAwLjcgMTAxLjE3QzExMDIuNyA5OC41ODUgMTEwNi4wOSA5Ni4xOTkgMTExMS4wOCA5NC4yMTFDMTExMi40OCA5My42MTUgMTExMy44OCA5My4yMTcgMTExNS44NyA5Mi42MkMxMTE3Ljg3IDkyLjAyNCAxMTE5Ljg3IDkxLjQyOCAxMTIxLjg2IDkwLjYzMlYxMTQuNDlaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTExOTQuOTIgODUuODYxTDExODguOTMgODQuMDcxQzExODMuNzMgODIuMjgyIDExODAuMzQgODAuNjkxIDExNzguMzQgNzkuMTAxQzExNzYuNTQgNzcuMzExIDExNzUuNTQgNzUuMTI0IDExNzUuNTQgNzIuNTRDMTE3NS41NCA2OS41NTcgMTE3Ni43NCA2Ny4zNyAxMTc4Ljk0IDY1LjU4MUMxMTgxLjE0IDYzLjc5MiAxMTg0LjMzIDYyLjk5NiAxMTg4LjMyIDYyLjk5NkMxMTkxLjcyIDYyLjk5NiAxMTk0LjkyIDYzLjU5MyAxMTk3LjcxIDY0Ljc4NkwxMjAwLjUxIDc3LjUxSDEyMTAuNDlMMTIxMS4yOSA2MS42MDVDMTIwNy42OSA1OS42MTYgMTIwNC4xIDU4LjAyNiAxMjAwLjUxIDU3LjAzMkMxMTk2LjkxIDU1LjgzOSAxMTkzLjEyIDU1LjQ0MSAxMTg4LjczIDU1LjQ0MUMxMTgyLjUzIDU1LjQ0MSAxMTc3LjM0IDU2LjQzNSAxMTcyLjk1IDU4LjYyMkMxMTY4Ljc2IDYwLjYxMSAxMTY1LjU2IDYzLjM5NCAxMTYzLjM3IDY2Ljk3M0MxMTYxLjE3IDcwLjM1MyAxMTU5Ljk3IDc0LjEzIDExNTkuOTcgNzguNTA0QzExNTkuOTcgODMuODczIDExNjEuNTcgODguMjQ2IDExNjQuNzYgOTEuODI1QzExNjguMTYgOTUuNDA0IDExNzIuNTUgOTcuOTg5IDExNzguMTQgOTkuNzc4TDExODUuNzMgMTAyLjM2M0MxMTkwLjUyIDEwMy45NTMgMTE5My45MiAxMDUuNzQzIDExOTUuOTEgMTA3LjUzMkMxMTk3LjkxIDEwOS4zMjEgMTE5OC45MSAxMTEuNTA4IDExOTguOTEgMTE0LjI5MUMxMTk4LjkxIDExNy40NzMgMTE5Ny43MSAxMjAuMDU3IDExOTUuMTEgMTIxLjg0N0MxMTkyLjUyIDEyMy42MzYgMTE4OC43MyAxMjQuNjMgMTE4My41MyAxMjQuNjNDMTE3OS4zNCAxMjQuNjMgMTE3NS4zNSAxMjMuODM1IDExNzEuNzUgMTIyLjQ0M0wxMTY4Ljk2IDEwOC41MjZIMTE1OC43N0wxMTU4Ljk3IDEyNi4wMjJDMTE2Mi43NyAxMjguMjA5IDExNjYuNTYgMTI5LjYwMSAxMTcwLjU1IDEzMC41OTVDMTE3NC41NSAxMzEuNzg4IDExNzguNzQgMTMyLjE4NSAxMTgzLjMzIDEzMi4xODVDMTE5My41MiAxMzIuMTg1IDEyMDEuMyAxMjkuOTk4IDEyMDYuNyAxMjUuNjI0QzEyMTIuMjggMTIxLjI1IDEyMTUuMDggMTE1LjY4MyAxMjE1LjA4IDEwOC45MjRDMTIxNS4wOCAxMDMuNzU0IDEyMTMuNDkgOTkuMTgxIDEyMTAuNDkgOTUuNjAzQzEyMDcuNDkgOTEuNDI4IDEyMDIuMyA4OC4yNDYgMTE5NC45MiA4NS44NjFaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTEyOTIuMTcgODUuNjYyQzEyOTIuMTcgNzkuNDk5IDEyOTAuOTcgNzQuMTMgMTI4OC4zNyA2OS43NTZDMTI4NS45OCA2NS4xODQgMTI4Mi41OCA2MS44MDQgMTI3OC4xOSA1OS4yMTlDMTI3My44IDU2LjYzNCAxMjY4LjYgNTUuNDQxIDEyNjIuNjEgNTUuNDQxQzEyNTYuMjMgNTUuNDQxIDEyNTAuMjQgNTcuMDMyIDEyNDQuNjQgNjAuMDE0QzEyMzkuMDUgNjIuOTk2IDEyMzQuNDYgNjcuMzcgMTIzMS4wNyA3My4zMzVDMTIyNy42NyA3OS4xMDEgMTIyNS44OCA4NS44NjEgMTIyNS44OCA5NC4wMTJDMTIyNS44OCAxMDEuOTY1IDEyMjcuNDcgMTA4LjUyNiAxMjMwLjQ3IDExNC4yOTFDMTIzMy40NiAxMTkuODU5IDEyMzcuNjYgMTI0LjIzMyAxMjQzLjA0IDEyNy4yMTVDMTI0OC40NCAxMzAuMTk3IDEyNTQuNjMgMTMxLjc4OCAxMjYxLjYyIDEzMS43ODhDMTI2OC42IDEzMS43ODggMTI3NC43OSAxMzAuMTk3IDEyNzkuNzkgMTI3LjIxNUMxMjg0Ljk4IDEyNC4wMzQgMTI4OC45NyAxMTkuODU5IDEyOTEuOTcgMTE0LjI5MUwxMjg3LjU3IDExMC4zMTVDMTI4NC45OCAxMTMuMDk5IDEyODIuMTggMTE1LjQ4NSAxMjc5LjE5IDExNy4yNzRDMTI3Ni4xOSAxMTkuMDYzIDEyNzIuNCAxMTkuODU5IDEyNjguMDEgMTE5Ljg1OUMxMjYxLjYyIDExOS44NTkgMTI1Ni40MyAxMTcuNjcxIDEyNTIuMDMgMTEzLjI5OEMxMjQ3Ljg0IDEwOC45MjQgMTI0NS42NCAxMDIuNTYxIDEyNDUuMjQgOTMuODEzSDEyOTEuNTdDMTI5MS45NyA5MS42MjYgMTI5Mi4xNyA4OC44NDMgMTI5Mi4xNyA4NS42NjJaTTEyNzMuMiA4NC40NjlDMTI3MiA4Ni4wNTkgMTI2OS42IDg2LjY1NiAxMjY2LjAxIDg2LjY1NkgxMjQ1LjI0QzEyNDUuNjQgODAuNjkxIDEyNDYuNjQgNzUuOTIgMTI0OC4yNCA3Mi4zNDFDMTI1MC4wMyA2OC43NjIgMTI1Mi4wMyA2Ni4zNzYgMTI1NC4yMyA2NC43ODZDMTI1Ni42MiA2My4xOTUgMTI1OS4wMiA2Mi40IDEyNjEuNDIgNjIuNEMxMjY1LjIxIDYyLjQgMTI2OC40IDYzLjc5MiAxMjcxIDY2Ljc3NEMxMjczLjU5IDY5Ljc1NiAxMjc1IDczLjUzNCAxMjc1IDc4LjEwN0MxMjc1IDgwLjg5IDEyNzQuMzkgODMuMDc3IDEyNzMuMiA4NC40NjlaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTY5OS4xNTYgMTIyLjQ0MkM2OTYuNzYgMTIyLjQ0MiA2OTQuNzYyIDEyMS42NDYgNjkzLjE2NiAxMTkuODU3QzY5MS43NjkgMTE4LjA2OCA2OTAuOTY5IDExNS40ODMgNjkwLjk2OSAxMTEuNzA2VjY3LjM2OUg3MDkuMzQxVjU4LjAyNEg2OTEuMTY4TDY5MS43NjkgMzcuMzQ4SDY3OS41ODdMNjczLjggNTguMDI0TDY2MS42MTcgNTkuNjE1VjY3LjM2OUg2NzIuODAxVjk5LjM3OUM2NzIuODAxIDEwMi4zNjEgNjcyLjgwMSAxMDQuNzQ3IDY3Mi41OTggMTA2LjkzNFYxMTMuNDk1QzY3Mi41OTggMTIwLjA1NiA2NzQuMzk3IDEyNS4wMjYgNjc3Ljc5MiAxMjguMDA4QzY4MS4xODYgMTMwLjk5MSA2ODUuOTc4IDEzMi41ODEgNjkxLjk2OCAxMzIuNTgxQzY5Ni43NiAxMzIuNTgxIDcwMC43NTIgMTMxLjc4NiA3MDQuMTQ3IDEyOS45OTdDNzA3LjU0MiAxMjguMjA3IDcxMC4xMzcgMTI1LjgyMiA3MTEuOTM2IDEyMi42NDFMNzA4LjM0MiAxMTguODYzQzcwNS4xNDYgMTIxLjA1IDcwMS45NSAxMjIuMjQzIDY5OS4xNTYgMTIyLjQ0MloiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMTM1NS42NiA5NS4wMDZDMTM1Mi40NiA5MS4yMjggMTM0Ny4yNyA4OC4yNDYgMTMzOS44OCA4NS42NjFMMTMzMy44OSA4My44NzJDMTMyOC43IDgyLjA4MyAxMzI1LjMxIDgwLjQ5MiAxMzIzLjMxIDc4LjkwMUMxMzIxLjUxIDc3LjExMiAxMzIwLjUxIDc0LjkyNSAxMzIwLjUxIDcyLjM0QzEzMjAuNTEgNjkuMzU4IDEzMjEuNzEgNjcuMTcxIDEzMjMuOTEgNjUuMzgyQzEzMjYuMTEgNjMuNTkzIDEzMjkuMyA2Mi43OTcgMTMzMy4yOSA2Mi43OTdDMTMzNi42OSA2Mi43OTcgMTMzOS44OCA2My4zOTQgMTM0Mi42OCA2NC41ODZMMTM0NS40NyA3Ny4zMTFIMTM1NS40NkwxMzU2LjI1IDYxLjQwNUMxMzUyLjY2IDU5LjQxNyAxMzQ5LjA3IDU3LjgyNyAxMzQ1LjQ3IDU2LjgzM0MxMzQxLjg4IDU1LjY0IDEzMzguMDkgNTUuMjQyIDEzMzMuNjkgNTUuMjQyQzEzMjcuNSA1NS4yNDIgMTMyMi4zMSA1Ni4yMzYgMTMxNy45MiA1OC40MjNDMTMxMy43MiA2MC40MTEgMTMxMC41MyA2My4xOTUgMTMwOC4zNCA2Ni43NzRDMTMwNi4xNCA3MC4xNTQgMTMwNC45NCA3My45MzEgMTMwNC45NCA3OC4zMDVDMTMwNC45NCA4My42NzMgMTMwNi41NCA4OC4wNDcgMTMwOS43MyA5MS42MjZDMTMxMy4xMyA5NS4yMDUgMTMxNy41MiA5Ny43ODkgMTMyMy4xMSA5OS41NzlMMTMzMC43IDEwMi4xNjNDMTMzNS40OSAxMDMuNzU0IDEzMzguODkgMTA1LjU0MyAxMzQwLjg4IDEwNy4zMzNDMTM0Mi44OCAxMDkuMTIyIDEzNDMuODggMTExLjMwOSAxMzQzLjg4IDExNC4wOTJDMTM0My44OCAxMTcuMjczIDEzNDIuNjggMTE5Ljg1OCAxMzQwLjA4IDEyMS42NDdDMTMzNy40OCAxMjMuNDM3IDEzMzMuNjkgMTI0LjQzMSAxMzI4LjUgMTI0LjQzMUMxMzI0LjMxIDEyNC40MzEgMTMyMC4zMSAxMjMuNjM1IDEzMTYuNzIgMTIyLjI0NEwxMzEzLjkzIDEwOC4zMjdIMTMwMy43NEwxMzAzLjk0IDEyNS44MjNDMTMwNy43MyAxMjguMDEgMTMxMS41MyAxMjkuNDAxIDEzMTUuNTIgMTMwLjM5NUMxMzE5LjUxIDEzMS41ODggMTMyMy43MSAxMzEuOTg2IDEzMjguMyAxMzEuOTg2QzEzMzguNDggMTMxLjk4NiAxMzQ2LjI3IDEyOS43OTkgMTM1MS42NiAxMjUuNDI1QzEzNTcuMjUgMTIxLjA1MSAxMzYwLjA1IDExNS40ODQgMTM2MC4wNSAxMDguNzI0QzEzNjAuNDUgMTAzLjM1NiAxMzU4Ljg1IDk4Ljc4MyAxMzU1LjY2IDk1LjAwNloiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNNzU0LjI1OSA4Ni40NTFMNzQ4LjI2OSA4NC42NjJDNzQzLjA3NSA4Mi44NzIgNzM5LjY4MSA4MS4yODIgNzM3LjY4NiA3OS42OTFDNzM1Ljg4OCA3Ny45MDIgNzM0Ljg4OSA3NS43MTUgNzM0Ljg4OSA3My4xM0M3MzQuODg5IDcwLjE0OCA3MzYuMDg3IDY3Ljk2MSA3MzguMjg0IDY2LjE3MkM3NDAuNDggNjQuMzgyIDc0My42NzYgNjMuNTg3IDc0Ny42NjggNjMuNTg3Qzc1MS4wNjMgNjMuNTg3IDc1NC4yNTkgNjQuMTgzIDc1Ny4wNTMgNjUuMzc2TDc1OS44NDcgNzguMUg3NjkuODMzTDc3MC42MzIgNjIuMzk0Qzc2Ny4wMzUgNjAuNDA2IDc2My40NDEgNTguODE1IDc1OS44NDcgNTcuODIxQzc1Ni4yNTMgNTYuNjI4IDc1Mi40NiA1Ni4yMyA3NDguMDY2IDU2LjIzQzc0MS44NzggNTYuMjMgNzM2LjY4OCA1Ny4yMjUgNzMyLjI5NCA1OS40MTJDNzI4LjEwMyA2MS40IDcyNC45MDcgNjQuMTgzIDcyMi43MSA2Ny43NjJDNzIwLjUxMyA3MS4xNDIgNzE5LjMxNSA3NC45MTkgNzE5LjMxNSA3OS4yOTNDNzE5LjMxNSA4NC42NjIgNzIwLjkxMSA4OS4wMzYgNzI0LjEwNyA5Mi42MTRDNzI3LjUwMiA5Ni4xOTMgNzMxLjg5NiA5OC43NzggNzM3LjQ4NCAxMDAuNTY3TDc0NS4wNzMgMTAzLjE1MkM3NDkuODY1IDEwNC43NDIgNzUzLjI2IDEwNi41MzIgNzU1LjI1OCAxMDguMzIxQzc1Ny4yNTIgMTEwLjExIDc1OC4yNTEgMTEyLjI5NyA3NTguMjUxIDExNS4wODFDNzU4LjI1MSAxMTguMjYyIDc1Ny4wNTMgMTIwLjg0NyA3NTQuNDU4IDEyMi42MzZDNzUxLjg2MyAxMjQuNDI1IDc0OC4wNjYgMTI1LjQxOSA3NDIuODc2IDEyNS40MTlDNzM4LjY4MiAxMjUuNDE5IDczNC42OSAxMjQuNjI0IDczMS4wOTYgMTIzLjIzMkw3MjguMzAyIDEwOS4zMTVINzE4LjExN0w3MTguMzE2IDEyNi44MTFDNzIyLjEwOSAxMjguOTk4IDcyNS45MDYgMTMwLjM5IDcyOS44OTggMTMxLjM4NEM3MzMuODkgMTMyLjU3NyA3MzguMDg1IDEzMi45NzQgNzQyLjY3NyAxMzIuOTc0Qzc1Mi44NTggMTMyLjk3NCA3NjAuNjQ3IDEzMC43ODcgNzY2LjA0IDEyNi40MTNDNzcxLjYyOCAxMjIuMDM5IDc3NC40MjUgMTE2LjQ3MiA3NzQuNDI1IDEwOS43MTNDNzc0LjQyNSAxMDQuNTQzIDc3Mi44MjYgOTkuOTcxIDc2OS44MzMgOTYuMzkyQzc2Ni44MzYgOTIuMDE4IDc2MS42NDYgODguODM3IDc1NC4yNTkgODYuNDUxWiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xMDYxLjE2IDEwOS4zMTdWNzcuOTAzTDEwNjEuNTYgNTYuNjNMMTA1OS4xNiA1NS4wMzlMMTAzMi4wMSA2NC41ODNWNzAuMzQ4TDEwNDIuNzkgNzEuNzRDMTA0Mi45OSA3NC43MjIgMTA0Mi45OSA3Ny43MDQgMTA0Mi45OSA4MC40ODhDMTA0My4xOSA4My4yNzIgMTA0My4xOSA4Ni42NTEgMTA0My4xOSA5MC42MjhWMTA5LjExOEMxMDQzLjE5IDExMy40OTIgMTA0My4xOSAxMTcuNDY4IDEwNDIuOTkgMTIxLjI0NkwxMDMzLjAxIDEyMy4yMzRWMTI5LjM5N0gxMDcwLjU0VjEyMy4yMzRMMTA2MS4zNiAxMjEuNDQ1QzEwNjEuMTYgMTE3LjY2NyAxMDYxLjE2IDExMy42OTEgMTA2MS4xNiAxMDkuMzE3WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik04NzMuODY3IDY5Ljk0N0w4ODUuNjQ4IDcxLjkzNUM4ODQuNDUgNzcuMzAzIDg4My4wNTMgODIuMjc0IDg4MS4yNTQgODYuODQ2Qzg3OS40NTkgOTEuMjIgODc3LjQ2MSA5NS41OTQgODc0LjY2NyAxMDAuMTY3Qzg3Mi4wNjggOTcuNTgyIDg2OS42NzIgOTQuOTk4IDg2Ny4wNzcgOTIuMjE0Qzg2NC40ODIgODkuNDMxIDg2MS44ODcgODYuNDQ5IDg1OC44OSA4My4yNjdDODU2LjI5NSA4MC40ODQgODU0LjA5OSA3OC4wOTggODUyLjEwMSA3Ni4xMUM4NTAuMTA3IDczLjkyMyA4NDguNTA3IDcyLjEzNCA4NDcuMTEgNzAuNTQzQzg1NC44OTggNjYuNzY2IDg2MC40OSA2Mi45ODggODY0LjI4MyA1OS4wMTJDODY3Ljg3NyA1NS4wMzUgODY5LjY3MiA1MC40NjIgODY5LjY3MiA0NS4yOTNDODY5LjY3MiAzOS41MjcgODY3LjQ3NSAzNC45NTUgODYzLjI4NCAzMS4zNzZDODU5LjA4OSAyNy43OTcgODUyLjkgMjYuMDA4IDg0NC45MTMgMjYuMDA4QzgzNi45MjkgMjYuMDA4IDgzMC43MzYgMjcuOTk2IDgyNS45NDQgMzEuOTcyQzgyMC45NTMgMzUuOTQ5IDgxOC41NTcgNDEuNTE2IDgxOC41NTcgNDguNDc0QzgxOC41NTcgNTIuMjUyIDgxOS4zNTcgNTYuMjI4IDgyMC43NTQgNjAuMDA2QzgyMi4xNTEgNjMuOTgyIDgyNC43NDYgNjcuOTU5IDgyOC4zNCA3Mi4zMzJDODI4LjUzOSA3Mi41MzEgODI4Ljc0MiA3Mi41MzEgODI4Ljc0MiA3Mi43M0M4MjguOTQxIDcyLjkyOSA4MjguOTQxIDcyLjkyOSA4MjkuMTQgNzMuMTI4QzgyMS4zNTIgNzYuOTA1IDgxNS41NjEgODEuMDggODExLjc2OCA4Ni4wNTFDODA3Ljk3NSA5MC44MjIgODA2LjE4IDk2LjM5IDgwNi4xOCAxMDIuNzUyQzgwNi4xOCAxMDcuNzIyIDgwNy4zNzggMTEyLjA5NiA4MDkuOTczIDExNi4yNzFDODEyLjU2OCAxMjAuMjQ4IDgxNi4xNjIgMTIzLjYyOCA4MjAuOTUzIDEyNi4wMTRDODI1Ljc0NSAxMjguMzk5IDgzMS4zMzcgMTI5LjU5MiA4MzcuNzI1IDEyOS41OTJDODQ0LjkxMyAxMjkuNTkyIDg1MC45MDMgMTI4LjM5OSA4NTUuNjk1IDEyNi4yMTJDODYwLjQ5IDEyMy44MjYgODY0LjQ4MiAxMjEuMDQzIDg2Ny42NzggMTE3Ljg2MkM4NjguNDc0IDExOC42NTcgODY5LjA3NSAxMTkuMjU0IDg2OS44NzEgMTIwLjA0OUM4NzAuNjcxIDEyMC44NDQgODcxLjQ3MSAxMjEuNDQxIDg3Mi4wNjggMTIyLjIzNkM4NzUuMDY1IDEyNS4wMTkgODc4LjA1OCAxMjcuMDA4IDg4MS4wNTUgMTI4LjAwMUM4ODQuMDQ4IDEyOS4xOTUgODg3LjY0NSAxMjkuNTkyIDg5Mi4wMzUgMTI5LjU5MkM4OTQuMjMyIDEyOS41OTIgODk2LjAzMSAxMjkuMzkzIDg5OC4wMjUgMTI5LjE5NUM5MDAuMDIzIDEyOC45OTYgOTAyLjIyIDEyOC41OTggOTA1LjIxMyAxMjcuODAzTDkwNi4yMTIgMTE5LjQ1M0w4OTEuNjM3IDExNi44NjhDODg5LjQ0IDExNC40ODIgODg3LjQ0MyAxMTIuNDk0IDg4NS40NDggMTEwLjMwN0M4ODMuNDUxIDEwOC4zMTkgODgxLjY1MiAxMDYuMzMgODc5Ljg1NyAxMDQuMzQyQzg4My40NTEgOTkuMTczIDg4Ni40NDQgOTQuMDA0IDg4OC44NDMgODguODM0Qzg5MS40MzggODMuNjY1IDg5My42MzUgNzcuNzAxIDg5NS40MyA3MS4xNEw5MDYuNDExIDY5LjM1VjYyLjc4OUg4NzQuNDY0TDg3My44NjcgNjkuOTQ3Wk04MzYuMzI4IDM1LjM1MkM4MzguNzI0IDMyLjk2NiA4NDEuNTE4IDMxLjc3NCA4NDQuOTEzIDMxLjc3NEM4NDguMzA4IDMxLjc3NCA4NTEuMTA1IDMyLjk2NiA4NTMuMjk5IDM1LjE1M0M4NTUuNDk2IDM3LjM0IDg1Ni42OTMgNDAuMzIzIDg1Ni42OTMgNDQuMjk5Qzg1Ni42OTMgNDguMDc3IDg1NS40OTYgNTEuNjU1IDg1My4yOTkgNTUuMjM0Qzg1MC45MDMgNTguODEzIDg0Ny43MTEgNjIuMzkxIDg0My43MTUgNjUuOTdDODQyLjkxOSA2NC45NzYgODQyLjExOSA2My45ODIgODQxLjUxOCA2My4xODdDODQwLjcyMiA2Mi4xOTMgODQwLjEyMSA2MS4zOTcgODM5LjMyNSA2MC40MDRDODM2LjkyOSA1Ny4yMjIgODM1LjMyOSA1NC4yNCA4MzQuNTMzIDUxLjg1NEM4MzMuNzMzIDQ5LjI3IDgzMy4zMzUgNDYuODg0IDgzMy4zMzUgNDQuNDk4QzgzMi45MzMgNDAuOTE5IDgzNC4xMzEgMzcuOTM3IDgzNi4zMjggMzUuMzUyWk04NDQuNzE0IDExOS4wNTVDODQwLjMyIDExOS4wNTUgODM2LjUyNyAxMTguMDYxIDgzMy4xMzIgMTE2LjI3MUM4MjkuOTQgMTE0LjI4MyA4MjcuMzQxIDExMS44OTcgODI1LjU0NiAxMDguNTE4QzgyMy43NDcgMTA1LjMzNiA4MjIuNzUyIDEwMS43NTggODIyLjc1MiA5Ny45OEM4MjIuNzUyIDk0LjQwMSA4MjMuNTQ4IDkxLjAyMSA4MjQuOTQ1IDg3LjQ0M0M4MjYuMzQ2IDgzLjg2NCA4MjguOTQxIDgwLjY4MyA4MzIuNzM0IDc3Ljg5OUM4MzQuNzMyIDgwLjI4NSA4MzYuOTI5IDgzLjA2OSA4MzkuMzI1IDg2LjA1MUM4NDEuOTIgODkuMDMzIDg0NC45MTMgOTIuNjEyIDg0OC4zMDggOTYuNzg3Qzg1MC41MDUgOTkuMzcyIDg1Mi43MDEgMTAyLjE1NSA4NTUuMDk3IDEwNC45MzlDODU3LjQ5MyAxMDcuNzIyIDg2MC4wODggMTEwLjUwNiA4NjIuNjgzIDExMy4yODlDODU3LjY5MiAxMTcuMDY2IDg1MS43MDMgMTE4Ljg1NiA4NDQuNzE0IDExOS4wNTVaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTk5My4yNyA3Ni45MTNDMTAwMi4yNSA3NS4xMjMgMTAwOC42NCA3Mi4zNCAxMDEyLjIzIDY3Ljk2NkMxMDE1LjgzIDYzLjU5MiAxMDE3LjYzIDU4LjgyMSAxMDE3LjYzIDUzLjY1MUMxMDE3LjYzIDQ2LjY5MiAxMDE0LjgzIDQwLjkyNyAxMDA5LjI0IDM2LjU1M0MxMDAzLjY1IDMxLjk4IDk5NS4wNiAyOS43OTMgOTgzLjQ4IDI5Ljc5M0g5MzcuMTZWMzYuOTUxTDk0OS45NCAzOC4zNDJDOTUwLjEzIDQ0LjcwNCA5NTAuMTMgNTEuMjY1IDk1MC4xMyA1Ny42MjdWMTAyLjE2M0M5NTAuMTMgMTA4LjUyNSA5NDkuOTQgMTE0Ljg4NyA5NDkuOTQgMTIxLjI0OUw5MzcuMTYgMTIyLjY0MVYxMjkuNzk5SDk3OS4yOUM5ODcuNjcgMTI5Ljc5OSA5OTQuNjYgMTI5LjAwMyAxMDAwLjI1IDEyNy40MTNDMTAwNS44NSAxMjUuODIyIDEwMTAuNDQgMTIzLjYzNSAxMDEzLjYzIDEyMC44NTJDMTAxNy4wMyAxMTguMDY4IDEwMTkuNDIgMTE1LjA4NiAxMDIwLjgyIDExMS45MDVDMTAyMi40MiAxMDguNTI1IDEwMjMuMDIgMTA1LjM0NCAxMDIzLjAyIDEwMS45NjRDMTAyMy4wMiA5NS42MDIgMTAyMC42MiA5MC4yMzQgMTAxNi4wMyA4NS42NjFDMTAxMS40MyA4MS4wODggMTAwMy44NSA3OC4zMDUgOTkzLjI3IDc2LjkxM1pNOTY5LjcgNTYuNjMzQzk2OS45IDUwLjI3MSA5NjkuOSA0My45MDkgOTY5LjkgMzcuNTQ3SDk3Ny44OUM5ODQuNjggMzcuNTQ3IDk4OS44NyAzOC45MzggOTkzLjA3IDQxLjcyMkM5OTYuNDYgNDQuNTA2IDk5OC4yNiA0OC44OCA5OTguMjYgNTUuMDQzQzk5OC4yNiA2MS4yMDYgOTk2LjQ2IDY2LjE3NyA5OTIuODcgNjkuMzU4Qzk4OS4yNyA3Mi41MzkgOTgzLjQ4IDczLjkzMSA5NzUuNjkgNzMuOTMxSDk2OS41MUw5NjkuNyA1Ni42MzNaTTk3Ny4wOSAxMjEuODQ2SDk2OS45Qzk2OS43IDExNS40ODQgOTY5LjcgMTA5LjEyMSA5NjkuNyAxMDIuNTZWODEuNDg2SDk3Ni40OUM5ODUuNDggODEuNDg2IDk5Mi4wNyA4My4yNzUgOTk2LjI2IDg2LjY1NUMxMDAwLjQ1IDkwLjAzNSAxMDAyLjY1IDk1LjAwNSAxMDAyLjY1IDEwMS45NjRDMTAwMi42NSAxMTUuMDg2IDk5NC4yNiAxMjEuODQ2IDk3Ny4wOSAxMjEuODQ2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xNy4yNTkgMjEuNjI5QzIzLjI0OSAyMS42MjkgMjguMDQxIDE2Ljg1NyAyOC4wNDEgMTAuODkyNEMyOC4wNDEgNC45Mjc5IDIzLjI0OSAwLjE1NjE4OSAxNy4yNTkgMC4xNTYxODlDMTEuMjY4NyAwLjE1NjE4OSA2LjQ3NjU2IDQuOTI3OSA2LjQ3NjU2IDEwLjg5MjRDNi40NzY1NiAxNi44NTcgMTEuMjY4NyAyMS42MjkgMTcuMjU5IDIxLjYyOVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMjEuMDYzIDcwLjE1NUMzMC4yNDggNjcuOTY4IDM2LjAzOCA1OC44MjIgMzMuODQyIDQ5LjY3NkMzMS42NDYgNDAuNTMxIDIyLjQ2MSAzNC43NjUgMTMuMjc2IDM2Ljk1MkM0LjA5MDk3IDM5LjEzOSAtMS42OTk0MyA0OC4yODUgMC40OTY5NzIgNTcuNDNDMi42OTMyNyA2Ni43NzUgMTEuODc4MiA3Mi4zNDIgMjEuMDYzIDcwLjE1NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMjEuMDYzIDE1NS40NDhDMzAuMjQ4IDE1My4yNiAzNi4wMzggMTQ0LjExNSAzMy44NDIgMTM0Ljk2OUMzMS42NDYgMTI1LjgyNCAyMi40NjEgMTIwLjA1OCAxMy4yNzYgMTIyLjI0NUM0LjA5MDk3IDEyNC40MzIgLTEuNjk5NDMgMTMzLjU3OCAwLjQ5Njk3MiAxNDIuNzIzQzIuNjkzMjcgMTUxLjg2OSAxMS44NzgyIDE1Ny42MzUgMjEuMDYzIDE1NS40NDhaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTI3Ljg2OSA5Ni4xODVDMjcuODY5IDkwLjIyMSAyMy4wNzcgODUuNDQ5IDE3LjA4NyA4NS40NDlDMTEuMDk2OCA4NS40NDkgNi4zMDQ2OSA5MC4yMjEgNi4zMDQ2OSA5Ni4xODVDNi4zMDQ2OSAxMDIuMTUgMTEuMDk2OCAxMDYuOTIyIDE3LjA4NyAxMDYuOTIyQzIzLjA3NyAxMDYuOTIyIDI3Ljg2OSAxMDIuMTUgMjcuODY5IDk2LjE4NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNODIuOTc2OSA5NUM3My41OTE5IDk1IDY1LjgwNDkgMTAyLjU1NSA2NS44MDQ5IDExMi4wOThDNjUuODA0OSAxMjEuNDQzIDczLjM5MTkgMTI5LjE5NyA4Mi45NzY5IDEyOS4xOTdDOTIuMzYwOSAxMjkuMTk3IDEwMC4xNDggMTIxLjY0MSAxMDAuMTQ4IDExMi4wOThDOTkuOTQ3OSAxMDIuNTU1IDkyLjM2MDkgOTUgODIuOTc2OSA5NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNODIuOTc4MSAxNDMuOTAyQzc2Ljk4ODEgMTQzLjkwMiA3Mi4xOTUxIDE0OC42NzQgNzIuMTk1MSAxNTQuNjM5QzcyLjE5NTEgMTYwLjYwMyA3Ni45ODgxIDE2NS4zNzUgODIuOTc4MSAxNjUuMzc1Qzg4Ljk2ODEgMTY1LjM3NSA5My43NjAxIDE2MC42MDMgOTMuNzYwMSAxNTQuNjM5QzkzLjU2MDEgMTQ4LjY3NCA4OC43NjgxIDE0My45MDIgODIuOTc4MSAxNDMuOTAyWiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik04Mi45NzgxIDgwLjA4MkM4OC45NjgxIDgwLjA4MiA5My43NjAxIDc1LjMxIDkzLjc2MDEgNjkuMzQ1QzkzLjc2MDEgNjMuMzgxIDg4Ljk2ODEgNTguNjA5IDgyLjk3ODEgNTguNjA5Qzc2Ljk4ODEgNTguNjA5IDcyLjE5NTEgNjMuMzgxIDcyLjE5NTEgNjkuMzQ1QzcyLjE5NTEgNzUuMzEgNzYuOTg4MSA4MC4wODIgODIuOTc4MSA4MC4wODJaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTg0LjU2MDEgMzcuMzQ1QzkwLjM1MDEgMzYuMzUxIDk0LjM0MzEgMzAuOTgzIDkzLjM0NTEgMjUuMjE3QzkyLjM0NzEgMTkuNDUxIDg2Ljk1NjEgMTUuNDc1IDgxLjE2NTEgMTYuNDY5Qzc1LjM3NTEgMTcuNDYzIDcxLjM4MTEgMjIuODMxIDcyLjM4MDEgMjguNTk3QzczLjM3ODEgMzQuMzYzIDc4Ljc2OTEgMzguMTQgODQuNTYwMSAzNy4zNDVaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTE2MC42NDkgNjUuNTc5QzE2Ny4yMzggNTkuMDE4IDE2Ny4yMzggNDguMDgzIDE2MC42NDkgNDEuNTIyQzE1NC4wNiAzNC45NjEgMTQzLjA3OCAzNC45NjEgMTM2LjQ4OSA0MS41MjJDMTI5LjkgNDguMDgzIDEyOS45IDU5LjAxOCAxMzYuNDg5IDY1LjU3OUMxNDMuMDc4IDcyLjMzOSAxNTQuMDYgNzIuMzM5IDE2MC42NDkgNjUuNTc5WiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik0xNDguNjY1IDIxLjYyOUMxNTQuNjU1IDIxLjYyOSAxNTkuNDQ3IDE2Ljg1NyAxNTkuNDQ3IDEwLjg5MjRDMTU5LjQ0NyA0LjkyNzkgMTU0LjY1NSAwLjE1NjE4OSAxNDguNjY1IDAuMTU2MTg5QzE0Mi42NzUgMC4xNTYxODkgMTM3Ljg4MyA0LjkyNzkgMTM3Ljg4MyAxMC44OTI0QzEzNy44ODMgMTYuODU3IDE0Mi42NzUgMjEuNjI5IDE0OC42NjUgMjEuNjI5WiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik0xNDguNjY1IDg1LjY0OEMxNDIuNjc1IDg1LjY0OCAxMzcuODgzIDkwLjQyIDEzNy44ODMgOTYuMzg1QzEzNy44ODMgMTAyLjM0OSAxNDIuNjc1IDEwNy4xMjEgMTQ4LjY2NSAxMDcuMTIxQzE1NC42NTUgMTA3LjEyMSAxNTkuNDQ3IDEwMi4zNDkgMTU5LjQ0NyA5Ni4zODVDMTU5LjI0OCA5MC40MiAxNTQuNDU1IDg1LjY0OCAxNDguNjY1IDg1LjY0OFoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMTQ4LjY2NSAxMjguMjAzQzE0Mi42NzUgMTI4LjIwMyAxMzcuODgzIDEzMi45NzUgMTM3Ljg4MyAxMzguOTM5QzEzNy44ODMgMTQ0LjkwNCAxNDIuNjc1IDE0OS42NzUgMTQ4LjY2NSAxNDkuNjc1QzE1NC42NTUgMTQ5LjY3NSAxNTkuNDQ3IDE0NC45MDQgMTU5LjQ0NyAxMzguOTM5QzE1OS4yNDggMTMyLjk3NSAxNTQuNDU1IDEyOC4yMDMgMTQ4LjY2NSAxMjguMjAzWiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzdfMiI+PHJlY3Qgd2lkdGg9IjEzNjAiIGhlaWdodD0iMjY5IiBmaWxsPSJ3aGl0ZSI+PC9yZWN0PjwvY2xpcFBhdGg+PC9kZWZzPjwvc3ZnPg==" width="148" height="29" alt="Weights &amp; Biases by CoreWeave">
      <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" aria-hidden="true" focusable="false" viewBox="0 0 73 73" fill="none"><rect x="0.864258" y="0.141113" width="72" height="72" rx="36" fill="#EDE8FF" fill-opacity="0.12"></rect><path fill-rule="evenodd" clip-rule="evenodd" d="M25.1937 22.1411C23.2405 22.1411 21.6572 23.7244 21.6572 25.6776V42.6525C21.6572 44.6056 23.2405 46.1889 25.1937 46.1889H45.9477C46.6981 46.1889 47.4177 46.487 47.9483 47.0176L50.8632 49.9325C51.3088 50.3781 52.0706 50.0625 52.0706 49.4324V25.6776C52.0706 23.7244 50.4873 22.1411 48.5342 22.1411H25.1937ZM32.9738 33.8114C32.9738 34.7879 32.1822 35.5796 31.2056 35.5796C30.2291 35.5796 29.4374 34.7879 29.4374 33.8114C29.4374 32.8348 30.2291 32.0432 31.2056 32.0432C32.1822 32.0432 32.9738 32.8348 32.9738 33.8114ZM38.6322 33.8114C38.6322 34.7879 37.8405 35.5796 36.8639 35.5796C35.8874 35.5796 35.0957 34.7879 35.0957 33.8114C35.0957 32.8348 35.8874 32.0432 36.8639 32.0432C37.8405 32.0432 38.6322 32.8348 38.6322 33.8114ZM44.2905 33.8114C44.2905 34.7879 43.4988 35.5796 42.5222 35.5796C41.5457 35.5796 40.754 34.7879 40.754 33.8114C40.754 32.8348 41.5457 32.0432 42.5222 32.0432C43.4988 32.0432 44.2905 32.8348 44.2905 33.8114Z" fill="url(#cw-wb-traces-bubble)"></path><defs><linearGradient id="cw-wb-traces-bubble" x1="36.5536" y1="22.1411" x2="36.5536" y2="53.8211" gradientUnits="userSpaceOnUse"><stop offset="0.385417" stop-color="#FFCC33"></stop><stop offset="0.71875" stop-color="#FFAD33"></stop></linearGradient></defs></svg>
      <span class="cw-wb-title">Weave Traces</span>
      <span class="cw-wb-description">Inspect model calls<br>and debug agent code</span>
      <span class="cw-wb-docs">Read docs <span aria-hidden="true">↗</span></span>
    </a>""")
    return (wandb_traces_card,)


@app.cell(hide_code=True)
def _(wandb_traces_card):
    mo.hstack([
        mo.md("""
    ### Connect W&B

    Use your W&B entity, project and API key in the original form below, then
    press **Connect**. The connection is shared by direct planning and the
    code-writing agent. W&B Weave records model calls and Sandbox runs in that project.
    """),
        wandb_traces_card,
    ], align="start", widths=[0.72, 0.28], gap=1.5)
    return


@app.cell(hide_code=True)
def _():
    # ---------- 1. Setup W&B ----------
    wandb_connect_form = (
        mo.md("""
        - W&B entity *(team)*: {entity}
        - W&B project: {project}
        - W&B API key *(required)*: {api_key}
        """)
        .batch(
            entity=mo.ui.text(placeholder="your-wandb-entity" , full_width=True),
            project=mo.ui.text(value="servless-sandbox-tutorial", full_width=True),
            api_key=mo.ui.text(kind="password", placeholder="from wandb.ai/authorize", full_width=True),
        )
        .form(submit_button_label="Connect", bordered=False)
    )
    wandb_connect_form
    return (wandb_connect_form,)


@app.cell(hide_code=True)
def _(wandb_connect_form):
    _v = wandb_connect_form.value or {}
    ENTITY = _v.get("entity")
    PROJECT = _v.get("project")
    API_KEY = _v.get("api_key")
    mo.stop(
        not (ENTITY and PROJECT and API_KEY),
        mo.md("_Fill in the form above and press **Connect**._"),
    )

    os.environ["WANDB_API_KEY"] = API_KEY
    weave.init(f"{ENTITY}/{PROJECT}")
    weave_url = f"https://wandb.ai/{ENTITY}/{PROJECT}/weave"

    mo.callout(
        mo.md(
            f"✅ **Connected** — logging to `{ENTITY}/{PROJECT}`. "
            f"[Open Weave dashboard]({weave_url})"
        ),
        kind="success",
    )
    return API_KEY, ENTITY, PROJECT, weave_url


@app.cell(hide_code=True)
def wandb_inference_feature():
    # Official logo: https://site.wandb.ai/wp-content/uploads/2023/05/wb-cw.svg
    # Original icon and card styling: https://wandb.ai/site/inference/
    # Documentation: https://docs.wandb.ai/inference
    # Inline SVG keeps the icon available without fetching a remote image.
    wandb_inference_card = mo.Html(r"""<style>
    .cw-wb-inference-card {
      box-sizing: border-box; display: flex; flex-direction: column; align-items: center;
      gap: 10px; width: 180px; max-width: 100%; padding: 16px; margin-left: auto;
      background: #20242b; border: 1px solid #4b535c; border-radius: 8px;
      color: #fff !important; text-align: center; text-decoration: none !important;
      font-family: "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
      transition: transform .2s, border-color .2s;
    }
    .cw-wb-inference-card:hover {transform: translateY(-4px); border-color: #ffcc33;}
    .cw-wb-inference-card:focus-visible {outline: 3px solid #ffcc33; outline-offset: 4px;}
    .cw-wb-inference-card svg {display: block; flex-shrink: 0;}
    .cw-wb-inference-card .cw-wb-brand {display:block; width:148px; max-width:100%; height:auto; margin:0 0 4px;}
    .cw-wb-inference-card .cw-wb-title {font-size: 20px; line-height: 26px; font-weight: 400;}
    .cw-wb-inference-card .cw-wb-description {font-size: 13px; line-height: 17px; color: #aeb3bd;}
    .cw-wb-inference-card .cw-wb-docs {font-size: 12px; line-height: 18px; color: #ffcc33; font-weight: 600;}
    @media (prefers-reduced-motion: reduce) {
      .cw-wb-inference-card {transition: none;}
    }
    </style>
    <a class="cw-wb-inference-card" href="https://docs.wandb.ai/inference"
       target="_blank" rel="noopener noreferrer" aria-label="W&B Serverless Inference documentation">
      <img class="cw-wb-brand" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMzYwIiBoZWlnaHQ9IjI2OSIgdmlld0JveD0iMCAwIDEzNjAgMjY5IiBmaWxsPSJub25lIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfN18yKSI+PHBhdGggZD0iTTgzMC4wNDUgMjUyLjI4M0M4MjYuNzUyIDI1Mi4yODMgODIzLjczNyAyNTEuNTQ4IDgyMS4wMDEgMjUwLjA3OUM4MTguMzE2IDI0OC42MSA4MTYuMjM5IDI0Ni41MzIgODE0Ljc2OSAyNDMuODQ3TDgxNS43NTcgMjQyLjYzMVYyNTEuMzcxSDgwOC44NDFWMTkzLjgzOUg4MTUuOTA5VjIxOS4yMjNMODE0Ljg0NSAyMTcuNDc1QzgxNi4zNjUgMjE1LjA0MyA4MTguNDQzIDIxMy4xMTggODIxLjA3NyAyMTEuNjk5QzgyMy43MTIgMjEwLjIzIDgyNi43MjcgMjA5LjQ5NSA4MzAuMTIxIDIwOS40OTVDODMzLjk3MiAyMDkuNDk1IDgzNy40MTcgMjEwLjQzMiA4NDAuNDU3IDIxMi4zMDdDODQzLjU0OCAyMTQuMTgyIDg0NS45OCAyMTYuNzQgODQ3Ljc1MyAyMTkuOTgzQzg0OS41MjcgMjIzLjE3NSA4NTAuNDEzIDIyNi44MjMgODUwLjQxMyAyMzAuOTI3Qzg1MC40MTMgMjM0LjkzIDg0OS41MjcgMjM4LjU1MiA4NDcuNzUzIDI0MS43OTVDODQ1Ljk4IDI0NS4wMzggODQzLjU0OCAyNDcuNTk2IDg0MC40NTcgMjQ5LjQ3MUM4MzcuNDE3IDI1MS4zNDYgODMzLjk0NyAyNTIuMjgzIDgzMC4wNDUgMjUyLjI4M1pNODI5LjUxMyAyNDUuNDQzQzgzMi4wOTcgMjQ1LjQ0MyA4MzQuNDAzIDI0NC44MSA4MzYuNDI5IDI0My41NDNDODM4LjQ1NiAyNDIuMjc2IDg0MC4wMjcgMjQwLjU1NCA4NDEuMTQxIDIzOC4zNzVDODQyLjMwNyAyMzYuMTQ2IDg0Mi44ODkgMjMzLjY2MyA4NDIuODg5IDIzMC45MjdDODQyLjg4OSAyMjguMDkgODQyLjMwNyAyMjUuNjA3IDg0MS4xNDEgMjIzLjQ3OUM4NDAuMDI3IDIyMS4zIDgzOC40NTYgMjE5LjU3OCA4MzYuNDI5IDIxOC4zMTFDODM0LjQwMyAyMTYuOTk0IDgzMi4wOTcgMjE2LjMzNSA4MjkuNTEzIDIxNi4zMzVDODI2LjkyOSAyMTYuMzM1IDgyNC41OTkgMjE2Ljk2OCA4MjIuNTIxIDIxOC4yMzVDODIwLjQ5NSAyMTkuNTAyIDgxOC44NzMgMjIxLjI1IDgxNy42NTcgMjIzLjQ3OUM4MTYuNDkyIDIyNS42NTggODE1LjkwOSAyMjguMTQgODE1LjkwOSAyMzAuOTI3QzgxNS45MDkgMjMzLjY2MyA4MTYuNDkyIDIzNi4xNDYgODE3LjY1NyAyMzguMzc1QzgxOC44NzMgMjQwLjU1NCA4MjAuNDk1IDI0Mi4yNzYgODIyLjUyMSAyNDMuNTQzQzgyNC41OTkgMjQ0LjgxIDgyNi45MjkgMjQ1LjQ0MyA4MjkuNTEzIDI0NS40NDNaTTg2My40MjMgMjY4LjA5MUM4NjIuNTExIDI2OC4wOTEgODYxLjU5OSAyNjguMDE1IDg2MC42ODcgMjY3Ljg2M0M4NTkuNzc1IDI2Ny43MTEgODU4LjkxNCAyNjcuNDU4IDg1OC4xMDMgMjY3LjEwM1YyNjAuNzk1Qzg1OC42NiAyNjAuODk2IDg1OS4zNDQgMjYwLjk5OCA4NjAuMTU1IDI2MS4wOTlDODYxLjAxNiAyNjEuMjUxIDg2MS44NTIgMjYxLjMyNyA4NjIuNjYzIDI2MS4zMjdDODY1LjA0NCAyNjEuMzI3IDg2Ni44NDMgMjYwLjc5NSA4NjguMDU5IDI1OS43MzFDODY5LjMyNiAyNTguNzE4IDg3MC41MTYgMjU2Ljk0NCA4NzEuNjMxIDI1NC40MTFMODc0LjIxNSAyNDguMjU1TDg3NC4wNjMgMjU0LjQxMUw4NTYuNTgzIDIxMC40MDdIODY0LjI1OUw4NzcuODYzIDI0NS4zNjdIODc1LjU4M0w4ODkuMTExIDIxMC40MDdIODk2LjkzOUw4NzguNDcxIDI1Ni4yMzVDODc3LjYxIDI1OC40MTQgODc2LjQ5NSAyNjAuMzkgODc1LjEyNyAyNjIuMTYzQzg3My44MSAyNjMuOTg3IDg3Mi4xODggMjY1LjQzMSA4NzAuMjYzIDI2Ni40OTVDODY4LjMzOCAyNjcuNTU5IDg2Ni4wNTggMjY4LjA5MSA4NjMuNDIzIDI2OC4wOTFaTTk0Ny44MyAyNTIuMjgzQzk0My44MiAyNTIuMjgzIDk0MC4xMyAyNTEuNTc0IDkzNi43MyAyNTAuMTU1QzkzMy4zOSAyNDguNjg2IDkzMC40NSAyNDYuNjM0IDkyNy45MiAyNDMuOTk5QzkyNS40MyAyNDEuMzY0IDkyMy41MSAyMzguMjc0IDkyMi4xNCAyMzQuNzI3QzkyMC43NyAyMzEuMTggOTIwLjA5IDIyNy4zMDQgOTIwLjA5IDIyMy4wOTlDOTIwLjA5IDIxOC44NDMgOTIwLjc3IDIxNC45NDIgOTIyLjE0IDIxMS4zOTVDOTIzLjUxIDIwNy44NDggOTI1LjQzIDIwNC43NTggOTI3LjkyIDIwMi4xMjNDOTMwLjQgMTk5LjQ4OCA5MzMuMzQgMTk3LjQ2MiA5MzYuNzMgMTk2LjA0M0M5NDAuMTMgMTk0LjU3NCA5NDMuODIgMTkzLjgzOSA5NDcuODMgMTkzLjgzOUM5NTEuNzMgMTkzLjgzOSA5NTUuMjIgMTk0LjUyMyA5NTguMzIgMTk1Ljg5MUM5NjEuNDYgMTk3LjI1OSA5NjQuMDkgMTk5LjAzMiA5NjYuMjIgMjAxLjIxMUM5NjguNCAyMDMuMzkgOTY5Ljk0IDIwNS43MiA5NzAuODYgMjA4LjIwM0w5NjQuMDIgMjExLjMxOUM5NjIuNyAyMDguMTc4IDk2MC42NSAyMDUuNjQ0IDk1Ny44NiAyMDMuNzE5Qzk1NS4wNyAyMDEuNzQzIDk1MS43MyAyMDAuNzU1IDk0Ny44MyAyMDAuNzU1Qzk0My44OCAyMDAuNzU1IDk0MC4zNSAyMDEuNjkyIDkzNy4yNiAyMDMuNTY3QzkzNC4yMiAyMDUuNDQyIDkzMS44NCAyMDguMDUxIDkzMC4xMiAyMTEuMzk1QzkyOC40IDIxNC43MzkgOTI3LjU0IDIxOC42NCA5MjcuNTQgMjIzLjA5OUM5MjcuNTQgMjI3LjUwNyA5MjguNCAyMzEuMzgzIDkzMC4xMiAyMzQuNzI3QzkzMS44NCAyMzguMDcxIDkzNC4yMiAyNDAuNjggOTM3LjI2IDI0Mi41NTVDOTQwLjM1IDI0NC40MyA5NDMuODggMjQ1LjM2NyA5NDcuODMgMjQ1LjM2N0M5NTEuNzMgMjQ1LjM2NyA5NTUuMDcgMjQ0LjQwNCA5NTcuODYgMjQyLjQ3OUM5NjAuNjUgMjQwLjUwMyA5NjIuNyAyMzcuOTQ0IDk2NC4wMiAyMzQuODAzTDk3MC44NiAyMzcuOTE5Qzk2OS45NCAyNDAuNDAyIDk2OC40IDI0Mi43MzIgOTY2LjIyIDI0NC45MTFDOTY0LjA5IDI0Ny4wOSA5NjEuNDYgMjQ4Ljg2MyA5NTguMzIgMjUwLjIzMUM5NTUuMjIgMjUxLjU5OSA5NTEuNzMgMjUyLjI4MyA5NDcuODMgMjUyLjI4M1pNMTAwMS4xNCAyNTIuMjgzQzk5Ny4xOSAyNTIuMjgzIDk5My42MiAyNTEuMzcxIDk5MC40MyAyNDkuNTQ3Qzk4Ny4yNCAyNDcuNjcyIDk4NC43IDI0NS4xMTQgOTgyLjgzIDI0MS44NzFDOTgwLjk1IDIzOC42MjggOTgwLjAyIDIzNC45NTUgOTgwLjAyIDIzMC44NTFDOTgwLjAyIDIyNi43NDcgOTgwLjkzIDIyMy4wOTkgOTgyLjc1IDIxOS45MDdDOTg0LjYzIDIxNi43MTUgOTg3LjE2IDIxNC4xODIgOTkwLjM1IDIxMi4zMDdDOTkzLjU0IDIxMC40MzIgOTk3LjE0IDIwOS40OTUgMTAwMS4xNCAyMDkuNDk1QzEwMDUuMSAyMDkuNDk1IDEwMDguNjcgMjEwLjQzMiAxMDExLjg2IDIxMi4zMDdDMTAxNS4wNSAyMTQuMTMxIDEwMTcuNTYgMjE2LjYzOSAxMDE5LjM4IDIxOS44MzFDMTAyMS4yNiAyMjMuMDIzIDEwMjIuMiAyMjYuNjk2IDEwMjIuMiAyMzAuODUxQzEwMjIuMiAyMzUuMDA2IDEwMjEuMjMgMjM4LjcwNCAxMDE5LjMxIDI0MS45NDdDMTAxNy4zOCAyNDUuMTM5IDEwMTQuODIgMjQ3LjY3MiAxMDExLjYzIDI0OS41NDdDMTAwOC40OSAyNTEuMzcxIDEwMDQuOTkgMjUyLjI4MyAxMDAxLjE0IDI1Mi4yODNaTTEwMDEuMTQgMjQ1LjQ0M0MxMDAzLjY4IDI0NS40NDMgMTAwNS45NiAyNDQuODEgMTAwNy45OCAyNDMuNTQzQzEwMTAuMDYgMjQyLjI3NiAxMDExLjY4IDI0MC41MjggMTAxMi44NSAyMzguMjk5QzEwMTQuMDYgMjM2LjA3IDEwMTQuNjcgMjMzLjU4NyAxMDE0LjY3IDIzMC44NTFDMTAxNC42NyAyMjguMDY0IDEwMTQuMDYgMjI1LjYwNyAxMDEyLjg1IDIyMy40NzlDMTAxMS42OCAyMjEuMyAxMDEwLjA2IDIxOS41NzggMTAwNy45OCAyMTguMzExQzEwMDUuOTYgMjE2Ljk5NCAxMDAzLjY4IDIxNi4zMzUgMTAwMS4xNCAyMTYuMzM1Qzk5OC41NiAyMTYuMzM1IDk5Ni4yMyAyMTYuOTk0IDk5NC4xNSAyMTguMzExQzk5Mi4xMyAyMTkuNTc4IDk5MC41IDIyMS4zIDk4OS4yOSAyMjMuNDc5Qzk4OC4wNyAyMjUuNjA3IDk4Ny40NiAyMjguMDY0IDk4Ny40NiAyMzAuODUxQzk4Ny40NiAyMzMuNTg3IDk4OC4wNyAyMzYuMDcgOTg5LjI5IDIzOC4yOTlDOTkwLjUgMjQwLjUyOCA5OTIuMTMgMjQyLjI3NiA5OTQuMTUgMjQzLjU0M0M5OTYuMjMgMjQ0LjgxIDk5OC41NiAyNDUuNDQzIDEwMDEuMTQgMjQ1LjQ0M1pNMTAzMy42OSAyNTEuMzcxVjIxMC40MDdIMTA0MC42MVYyMTcuOTMxTDEwMzkuODUgMjE2Ljg2N0MxMDQwLjgxIDIxNC41MzYgMTA0Mi4yOCAyMTIuODE0IDEwNDQuMjYgMjExLjY5OUMxMDQ2LjIzIDIxMC41MzQgMTA0OC42NCAyMDkuOTUxIDEwNTEuNDggMjA5Ljk1MUgxMDUzLjk5VjIxNi42MzlIMTA1MC40MUMxMDQ3LjUzIDIxNi42MzkgMTA0NS4yIDIxNy41NTEgMTA0My40MiAyMTkuMzc1QzEwNDEuNjUgMjIxLjE0OCAxMDQwLjc2IDIyMy42ODIgMTA0MC43NiAyMjYuOTc1VjI1MS4zNzFIMTAzMy42OVpNMTA4MS4zOSAyNTIuMjgzQzEwNzcuNDQgMjUyLjI4MyAxMDczLjkyIDI1MS4zNDYgMTA3MC44MyAyNDkuNDcxQzEwNjcuNzQgMjQ3LjU5NiAxMDY1LjMxIDI0NS4wMzggMTA2My41MyAyNDEuNzk1QzEwNjEuNzYgMjM4LjUwMiAxMDYwLjg3IDIzNC44MjggMTA2MC44NyAyMzAuNzc1QzEwNjAuODcgMjI2LjY3MSAxMDYxLjczIDIyMy4wMjMgMTA2My40NiAyMTkuODMxQzEwNjUuMjMgMjE2LjYzOSAxMDY3LjYxIDIxNC4xMzEgMTA3MC42IDIxMi4zMDdDMTA3My42NCAyMTAuNDMyIDEwNzcuMDQgMjA5LjQ5NSAxMDgwLjc4IDIwOS40OTVDMTA4My44MiAyMDkuNDk1IDEwODYuNTEgMjEwLjA1MiAxMDg4Ljg0IDIxMS4xNjdDMTA5MS4yMiAyMTIuMjMxIDEwOTMuMjIgMjEzLjcgMTA5NC44NCAyMTUuNTc1QzEwOTYuNTIgMjE3LjM5OSAxMDk3Ljc4IDIxOS41MDIgMTA5OC42NCAyMjEuODgzQzEwOTkuNTYgMjI0LjIxNCAxMTAwLjAxIDIyNi42NDYgMTEwMC4wMSAyMjkuMTc5QzExMDAuMDEgMjI5LjczNiAxMDk5Ljk2IDIzMC4zNyAxMDk5Ljg2IDIzMS4wNzlDMTA5OS44MSAyMzEuNzM4IDEwOTkuNzMgMjMyLjM3MSAxMDk5LjYzIDIzMi45NzlIMTA2Ni4wNFYyMjYuODk5SDEwOTUuNTNMMTA5Mi4xOCAyMjkuNjM1QzEwOTIuNjQgMjI3IDEwOTIuMzkgMjI0LjY0NCAxMDkxLjQyIDIyMi41NjdDMTA5MC40NiAyMjAuNDkgMTA4OS4wNCAyMTguODQzIDEwODcuMTcgMjE3LjYyN0MxMDg1LjI5IDIxNi40MTEgMTA4My4xNyAyMTUuODAzIDEwODAuNzggMjE1LjgwM0MxMDc4LjQgMjE1LjgwMyAxMDc2LjIyIDIxNi40MTEgMTA3NC4yNSAyMTcuNjI3QzEwNzIuMjcgMjE4Ljg0MyAxMDcwLjczIDIyMC41OTEgMTA2OS42MSAyMjIuODcxQzEwNjguNTUgMjI1LjEgMTA2OC4xMiAyMjcuNzYgMTA2OC4zMiAyMzAuODUxQzEwNjguMTIgMjMzLjg0IDEwNjguNTcgMjM2LjQ3NSAxMDY5LjY5IDIzOC43NTVDMTA3MC44NSAyNDAuOTg0IDEwNzIuNDggMjQyLjczMiAxMDc0LjU1IDI0My45OTlDMTA3Ni42OCAyNDUuMjE1IDEwNzguOTkgMjQ1LjgyMyAxMDgxLjQ3IDI0NS44MjNDMTA4NC4yIDI0NS44MjMgMTA4Ni41MSAyNDUuMTkgMTA4OC4zOCAyNDMuOTIzQzEwOTAuMjYgMjQyLjY1NiAxMDkxLjc4IDI0MS4wMzUgMTA5Mi45NCAyMzkuMDU5TDEwOTguODcgMjQyLjA5OUMxMDk4LjA2IDI0My45NzQgMTA5Ni44IDI0NS42OTYgMTA5NS4wNyAyNDcuMjY3QzEwOTMuNCAyNDguNzg3IDEwOTEuNCAyNTAuMDAzIDEwODkuMDcgMjUwLjkxNUMxMDg2Ljc5IDI1MS44MjcgMTA4NC4yMyAyNTIuMjgzIDEwODEuMzkgMjUyLjI4M1pNMTEyMi43NiAyNTEuMzcxTDExMDYuODcgMTk0Ljc1MUgxMTE0LjdMMTEyOCAyNDQuNjA3SDExMjYuMThMMTE0MC4wMSAxOTQuNzUxSDExNDcuODRMMTE2MS41OSAyNDQuNjA3SDExNTkuNjlMMTE3My4wNyAxOTQuNzUxSDExODAuOUwxMTY1LjAxIDI1MS4zNzFIMTE1Ni43M0wxMTQyLjkgMjAxLjc0M0gxMTQ0Ljg3TDExMzEuMDQgMjUxLjM3MUgxMTIyLjc2Wk0xMjA1LjUyIDI1Mi4yODNDMTIwMS41NyAyNTIuMjgzIDExOTguMDUgMjUxLjM0NiAxMTk0Ljk2IDI0OS40NzFDMTE5MS44NiAyNDcuNTk2IDExODkuNDMgMjQ1LjAzOCAxMTg3LjY2IDI0MS43OTVDMTE4NS44OSAyMzguNTAyIDExODUgMjM0LjgyOCAxMTg1IDIzMC43NzVDMTE4NSAyMjYuNjcxIDExODUuODYgMjIzLjAyMyAxMTg3LjU4IDIxOS44MzFDMTE4OS4zNiAyMTYuNjM5IDExOTEuNzQgMjE0LjEzMSAxMTk0LjczIDIxMi4zMDdDMTE5Ny43NyAyMTAuNDMyIDEyMDEuMTYgMjA5LjQ5NSAxMjA0LjkxIDIwOS40OTVDMTIwNy45NSAyMDkuNDk1IDEyMTAuNjQgMjEwLjA1MiAxMjEyLjk3IDIxMS4xNjdDMTIxNS4zNSAyMTIuMjMxIDEyMTcuMzUgMjEzLjcgMTIxOC45NyAyMTUuNTc1QzEyMjAuNjQgMjE3LjM5OSAxMjIxLjkxIDIxOS41MDIgMTIyMi43NyAyMjEuODgzQzEyMjMuNjggMjI0LjIxNCAxMjI0LjE0IDIyNi42NDYgMTIyNC4xNCAyMjkuMTc5QzEyMjQuMTQgMjI5LjczNiAxMjI0LjA5IDIzMC4zNyAxMjIzLjk5IDIzMS4wNzlDMTIyMy45NCAyMzEuNzM4IDEyMjMuODYgMjMyLjM3MSAxMjIzLjc2IDIzMi45NzlIMTE5MC4xN1YyMjYuODk5SDEyMTkuNjZMMTIxNi4zMSAyMjkuNjM1QzEyMTYuNzcgMjI3IDEyMTYuNTEgMjI0LjY0NCAxMjE1LjU1IDIyMi41NjdDMTIxNC41OSAyMjAuNDkgMTIxMy4xNyAyMTguODQzIDEyMTEuMyAyMTcuNjI3QzEyMDkuNDIgMjE2LjQxMSAxMjA3LjI5IDIxNS44MDMgMTIwNC45MSAyMTUuODAzQzEyMDIuNTMgMjE1LjgwMyAxMjAwLjM1IDIxNi40MTEgMTE5OC4zOCAyMTcuNjI3QzExOTYuNCAyMTguODQzIDExOTQuODUgMjIwLjU5MSAxMTkzLjc0IDIyMi44NzFDMTE5Mi42OCAyMjUuMSAxMTkyLjI0IDIyNy43NiAxMTkyLjQ1IDIzMC44NTFDMTE5Mi4yNCAyMzMuODQgMTE5Mi43IDIzNi40NzUgMTE5My44MiAyMzguNzU1QzExOTQuOTggMjQwLjk4NCAxMTk2LjYgMjQyLjczMiAxMTk4LjY4IDI0My45OTlDMTIwMC44MSAyNDUuMjE1IDEyMDMuMTEgMjQ1LjgyMyAxMjA1LjYgMjQ1LjgyM0MxMjA4LjMzIDI0NS44MjMgMTIxMC42NCAyNDUuMTkgMTIxMi41MSAyNDMuOTIzQzEyMTQuMzkgMjQyLjY1NiAxMjE1LjkxIDI0MS4wMzUgMTIxNy4wNyAyMzkuMDU5TDEyMjMgMjQyLjA5OUMxMjIyLjE5IDI0My45NzQgMTIyMC45MiAyNDUuNjk2IDEyMTkuMiAyNDcuMjY3QzEyMTcuNTMgMjQ4Ljc4NyAxMjE1LjUzIDI1MC4wMDMgMTIxMy4yIDI1MC45MTVDMTIxMC45MiAyNTEuODI3IDEyMDguMzYgMjUyLjI4MyAxMjA1LjUyIDI1Mi4yODNaTTEyNDcuMTIgMjUyLjI4M0MxMjQ0LjQ0IDI1Mi4yODMgMTI0Mi4wNiAyNTEuODAyIDEyMzkuOTggMjUwLjgzOUMxMjM3Ljk1IDI0OS44MjYgMTIzNi4zNiAyNDguNDU4IDEyMzUuMTkgMjQ2LjczNUMxMjM0LjAzIDI0NC45NjIgMTIzMy40NCAyNDIuOTM1IDEyMzMuNDQgMjQwLjY1NUMxMjMzLjQ0IDIzOC40NzYgMTIzMy45IDIzNi41MjYgMTIzNC44MSAyMzQuODAzQzEyMzUuNzcgMjMzLjAzIDEyMzcuMjQgMjMxLjUzNSAxMjM5LjIyIDIzMC4zMTlDMTI0MS4yNSAyMjkuMTAzIDEyNDMuNzggMjI4LjI0MiAxMjQ2LjgyIDIyNy43MzVMMTI2Mi4wMiAyMjUuMjI3VjIzMS4xNTVMMTI0OC40MiAyMzMuNDM1QzEyNDUuNzggMjMzLjg5MSAxMjQzLjg2IDIzNC43MjcgMTI0Mi42NCAyMzUuOTQzQzEyNDEuNDcgMjM3LjE1OSAxMjQwLjg5IDIzOC42NTQgMTI0MC44OSAyNDAuNDI3QzEyNDAuODkgMjQyLjA5OSAxMjQxLjU1IDI0My40OTIgMTI0Mi44NyAyNDQuNjA3QzEyNDQuMjQgMjQ1LjcyMiAxMjQ1LjkzIDI0Ni4yNzkgMTI0Ny45NiAyNDYuMjc5QzEyNTAuNTQgMjQ2LjI3OSAxMjUyLjc3IDI0NS43NDcgMTI1NC42NSAyNDQuNjgzQzEyNTYuNTcgMjQzLjU2OCAxMjU4LjA3IDI0Mi4wNzQgMTI1OS4xMyAyNDAuMTk5QzEyNjAuMjUgMjM4LjMyNCAxMjYwLjggMjM2LjI0NyAxMjYwLjggMjMzLjk2N1YyMjMuNTU1QzEyNjAuOCAyMjEuMzI2IDEyNTkuOTcgMjE5LjUyNyAxMjU4LjMgMjE4LjE1OUMxMjU2LjY3IDIxNi43NCAxMjU0LjUyIDIxNi4wMzEgMTI1MS44NCAyMTYuMDMxQzEyNDkuNSAyMTYuMDMxIDEyNDcuNDMgMjE2LjYzOSAxMjQ1LjYgMjE3Ljg1NUMxMjQzLjgzIDIxOS4wMiAxMjQyLjUxIDIyMC41OTEgMTI0MS42NSAyMjIuNTY3TDEyMzUuNSAyMTkuMzc1QzEyMzYuMjYgMjE3LjUgMTIzNy40NyAyMTUuODI4IDEyMzkuMTQgMjE0LjM1OUMxMjQwLjgyIDIxMi44MzkgMTI0Mi43NyAyMTEuNjQ4IDEyNDUgMjEwLjc4N0MxMjQ3LjIyIDIwOS45MjYgMTI0OS41NiAyMDkuNDk1IDEyNTEuOTkgMjA5LjQ5NUMxMjU1LjEzIDIwOS40OTUgMTI1Ny44OSAyMTAuMTAzIDEyNjAuMjcgMjExLjMxOUMxMjYyLjY1IDIxMi40ODQgMTI2NC41IDIxNC4xMzEgMTI2NS44MiAyMTYuMjU5QzEyNjcuMTkgMjE4LjMzNiAxMjY3Ljg3IDIyMC43NjggMTI2Ny44NyAyMjMuNTU1VjI1MS4zNzFIMTI2MC45NlYyNDMuNjE5TDEyNjIuMjUgMjQ0LjA3NUMxMjYxLjM5IDI0NS42OTYgMTI2MC4yMiAyNDcuMTE1IDEyNTguNzUgMjQ4LjMzMUMxMjU3LjI4IDI0OS41NDcgMTI1NS41NiAyNTAuNTEgMTI1My41OCAyNTEuMjE5QzEyNTEuNjEgMjUxLjkyOCAxMjQ5LjQ1IDI1Mi4yODMgMTI0Ny4xMiAyNTIuMjgzWk0xMjkxLjc3IDI1MS4zNzFMMTI3NS43MyAyMTAuNDA3SDEyODMuNjRMMTI5Ni40OCAyNDUuMDYzSDEyOTMuNzRMMTMwNi42NiAyMTAuNDA3SDEzMTQuNTdMMTI5OC40NiAyNTEuMzcxSDEyOTEuNzdaTTEzNDEuMjggMjUyLjI4M0MxMzM3LjMzIDI1Mi4yODMgMTMzMy44IDI1MS4zNDYgMTMzMC43MSAyNDkuNDcxQzEzMjcuNjIgMjQ3LjU5NiAxMzI1LjE5IDI0NS4wMzggMTMyMy40MiAyNDEuNzk1QzEzMjEuNjQgMjM4LjUwMiAxMzIwLjc2IDIzNC44MjggMTMyMC43NiAyMzAuNzc1QzEzMjAuNzYgMjI2LjY3MSAxMzIxLjYyIDIyMy4wMjMgMTMyMy4zNCAyMTkuODMxQzEzMjUuMTEgMjE2LjYzOSAxMzI3LjUgMjE0LjEzMSAxMzMwLjQ5IDIxMi4zMDdDMTMzMy41MyAyMTAuNDMyIDEzMzYuOTIgMjA5LjQ5NSAxMzQwLjY3IDIwOS40OTVDMTM0My43MSAyMDkuNDk1IDEzNDYuMzkgMjEwLjA1MiAxMzQ4LjczIDIxMS4xNjdDMTM1MS4xMSAyMTIuMjMxIDEzNTMuMTEgMjEzLjcgMTM1NC43MyAyMTUuNTc1QzEzNTYuNCAyMTcuMzk5IDEzNTcuNjcgMjE5LjUwMiAxMzU4LjUzIDIyMS44ODNDMTM1OS40NCAyMjQuMjE0IDEzNTkuOSAyMjYuNjQ2IDEzNTkuOSAyMjkuMTc5QzEzNTkuOSAyMjkuNzM2IDEzNTkuODUgMjMwLjM3IDEzNTkuNzUgMjMxLjA3OUMxMzU5LjY5IDIzMS43MzggMTM1OS42MiAyMzIuMzcxIDEzNTkuNTIgMjMyLjk3OUgxMzI1LjkzVjIyNi44OTlIMTM1NS40MUwxMzUyLjA3IDIyOS42MzVDMTM1Mi41MyAyMjcgMTM1Mi4yNyAyMjQuNjQ0IDEzNTEuMzEgMjIyLjU2N0MxMzUwLjM1IDIyMC40OSAxMzQ4LjkzIDIxOC44NDMgMTM0Ny4wNSAyMTcuNjI3QzEzNDUuMTggMjE2LjQxMSAxMzQzLjA1IDIxNS44MDMgMTM0MC42NyAyMTUuODAzQzEzMzguMjkgMjE1LjgwMyAxMzM2LjExIDIxNi40MTEgMTMzNC4xMyAyMTcuNjI3QzEzMzIuMTYgMjE4Ljg0MyAxMzMwLjYxIDIyMC41OTEgMTMyOS41IDIyMi44NzFDMTMyOC40MyAyMjUuMSAxMzI4IDIyNy43NiAxMzI4LjIxIDIzMC44NTFDMTMyOCAyMzMuODQgMTMyOC40NiAyMzYuNDc1IDEzMjkuNTcgMjM4Ljc1NUMxMzMwLjc0IDI0MC45ODQgMTMzMi4zNiAyNDIuNzMyIDEzMzQuNDQgMjQzLjk5OUMxMzM2LjU3IDI0NS4yMTUgMTMzOC44NyAyNDUuODIzIDEzNDEuMzUgMjQ1LjgyM0MxMzQ0LjA5IDI0NS44MjMgMTM0Ni4zOSAyNDUuMTkgMTM0OC4yNyAyNDMuOTIzQzEzNTAuMTQgMjQyLjY1NiAxMzUxLjY2IDI0MS4wMzUgMTM1Mi44MyAyMzkuMDU5TDEzNTguNzYgMjQyLjA5OUMxMzU3Ljk1IDI0My45NzQgMTM1Ni42OCAyNDUuNjk2IDEzNTQuOTYgMjQ3LjI2N0MxMzUzLjI5IDI0OC43ODcgMTM1MS4yOCAyNTAuMDAzIDEzNDguOTUgMjUwLjkxNUMxMzQ2LjY3IDI1MS44MjcgMTM0NC4xMSAyNTIuMjgzIDEzNDEuMjggMjUyLjI4M1oiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMTA1Mi4xOCA0MS4zMTZDMTA1NS4zNyA0MS4zMTYgMTA1OC4xNyA0MC4zMjIgMTA2MC4xNiAzOC4zMzRDMTA2Mi4zNiAzNi4zNDYgMTA2My41NSAzMy43NjEgMTA2My41NSAzMC41OEMxMDYzLjU1IDI3LjM5OSAxMDYyLjM2IDI0LjgxNCAxMDYwLjE2IDIyLjgyNkMxMDU3Ljk3IDIwLjgzOCAxMDU1LjM3IDE5Ljg0NCAxMDUyLjE4IDE5Ljg0NEMxMDQ4Ljk4IDE5Ljg0NCAxMDQ2LjE5IDIwLjgzOCAxMDQzLjk5IDIyLjgyNkMxMDQxLjc5IDI0LjgxNCAxMDQwLjU5IDI3LjM5OSAxMDQwLjU5IDMwLjU4QzEwNDAuNTkgMzMuNzYxIDEwNDEuNzkgMzYuMzQ2IDEwNDMuOTkgMzguMzM0QzEwNDYuMTkgNDAuMzIyIDEwNDguOTggNDEuMzE2IDEwNTIuMTggNDEuMzE2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik00MzcuMzc2IDg2LjI1MkM0MzcuMzc2IDgwLjA4OCA0MzYuMTc4IDc0LjcyIDQzMy41ODMgNzAuMzQ2QzQzMS4xODcgNjUuNzczIDQyNy43OTIgNjIuMzkzIDQyMy40MDIgNTkuODA5QzQxOS4wMDggNTcuMjI0IDQxMy44MTUgNTYuMDMxIDQwNy44MjUgNTYuMDMxQzQwMS40MzcgNTYuMDMxIDM5NS40NDcgNTcuNjIyIDM4OS44NTUgNjAuNjA0QzM4NC4yNjQgNjMuNTg2IDM3OS42NzEgNjcuOTYgMzc2LjI4IDczLjkyNUMzNzIuODg1IDc5LjY5MSAzNzEuMDg2IDg2LjQ1MSAzNzEuMDg2IDk0LjYwMkMzNzEuMDg2IDEwMi43NTMgMzcyLjY4NiAxMDkuMTE2IDM3NS42NzkgMTE0Ljg4MUMzNzguNjc2IDEyMC40NDggMzgyLjg2NyAxMjQuODIyIDM4OC4yNTkgMTI3LjgwNUMzOTMuNjQ4IDEzMC43ODcgMzk5Ljg0MSAxMzIuMzc3IDQwNi44MjYgMTMyLjM3N0M0MTMuODE1IDEzMi4zNzcgNDIwLjAwNyAxMzAuNzg3IDQyNC45OTggMTI3LjgwNUM0MzAuMTg4IDEyNC42MjMgNDM0LjE4NCAxMjAuNDQ4IDQzNy4xNzcgMTE0Ljg4MUw0MzIuNzgzIDExMC45MDVDNDMwLjE4OCAxMTMuNjg4IDQyNy4zOTQgMTE2LjA3NSA0MjQuMzk3IDExNy44NjRDNDIxLjQwNCAxMTkuNjUzIDQxNy42MTEgMTIwLjQ0OCA0MTMuMjE4IDEyMC40NDhDNDA2LjgyNiAxMjAuNDQ4IDQwMS42MzYgMTE4LjI2MSAzOTcuMjQyIDExMy44ODdDMzkzLjA1MSAxMDkuNTEzIDM5MC44NTQgMTAzLjE1MSAzOTAuNDU2IDk0LjQwM0g0MzYuNzc5QzQzNi45NzggOTIuMjE2IDQzNy4zNzYgODkuNDMzIDQzNy4zNzYgODYuMjUyWk00MTguNDA4IDg1LjI1N0M0MTcuMjEgODYuODQ4IDQxNC44MTQgODcuNDQ1IDQxMS4yMiA4Ny40NDVIMzkwLjQ1NkMzOTAuODU0IDgxLjQ4IDM5MS44NTMgNzYuNzA4IDM5My40NDkgNzMuMTI5QzM5NS4yNDggNjkuNTUxIDM5Ny4yNDIgNjcuMTY1IDM5OS40MzkgNjUuNTc0QzQwMS44MzUgNjMuOTg0IDQwNC4yMzEgNjMuMTg5IDQwNi42MjcgNjMuMTg5QzQxMC40MjQgNjMuMTg5IDQxMy42MTYgNjQuNTgxIDQxNi4yMTEgNjcuNTYzQzQxOC44MDkgNzAuNTQ1IDQyMC4yMDYgNzQuMzIyIDQyMC4yMDYgNzguODk1QzQyMC4wMDcgODEuNDggNDE5LjQwNyA4My42NjcgNDE4LjQwOCA4NS4yNTdaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTU0Ny44MSA2Mi4yMDFDNTQyLjYxNyA1OC4wMjUgNTM1LjQyOSA1NS44MzkgNTI2LjI0NyA1NS44MzlDNTE3LjA2MSA1NS44MzkgNTA5Ljg3MyA1OC4wMjUgNTA0LjY4IDYyLjU5OEM0OTkuNDkgNjYuOTcyIDQ5Ni44OTUgNzIuOTM3IDQ5Ni44OTUgODAuMjkzQzQ5Ni44OTUgOTAuMDM1IDUwMC44ODcgOTYuOTk0IDUwOC44NzUgMTAwLjk3QzUwNS4wODIgMTA0LjM1IDUwMi4yODQgMTA3LjUzMSA1MDAuNDg5IDExMC41MTRDNDk4LjY5IDExMy4yOTcgNDk3Ljg5NCAxMTYuMjc5IDQ5Ny44OTQgMTE5LjA2M0M0OTcuODk0IDEyMS44NDYgNDk4LjY5IDEyNC4yMzIgNTAwLjA4NyAxMjYuMjJDNTAxLjY4NyAxMjguMjA4IDUwMy44ODQgMTI5Ljc5OSA1MDcuMDc2IDEzMC43OTNDNTAyLjI4NCAxMzMuMTc5IDQ5OC42OSAxMzUuNTY1IDQ5Ni42OTYgMTM4LjE0OUM0OTQuNDk5IDE0MC45MzMgNDkzLjUgMTQzLjkxNSA0OTMuNSAxNDcuMDk2QzQ5My41IDE1MC4yNzcgNDk0LjQ5OSAxNTMuNDU4IDQ5Ni40OTMgMTU2LjA0M0M0OTguNjkgMTU4LjgyNyA1MDIuMDg1IDE2MC44MTQgNTA2LjY3OCAxNjIuNjA0QzUxMS40NyAxNjQuMTk0IDUxNy42NTggMTY0Ljk5IDUyNS40NDcgMTY0Ljk5QzUzNC40MzQgMTY0Ljk5IDU0MS44MjEgMTYzLjc5NyA1NDcuODEgMTYxLjIxMkM1NTMuOCAxNTguNjI4IDU1OC4zOTMgMTU1LjQ0NyA1NjEuMzg2IDE1MS4yNzFDNTY0LjU4MiAxNDcuMDk2IDU2NS45NzkgMTQyLjcyMiA1NjUuOTc5IDEzNy45NUM1NjUuOTc5IDEzMS41ODggNTYzLjc4MiAxMjYuNjE4IDU1OS41OTEgMTIyLjg0QzU1NS4zOTYgMTE5LjA2MyA1NDguNDA4IDExNy4yNzMgNTM4LjQyNiAxMTcuMjczSDUxOS40NTdDNTE2LjA2MiAxMTcuMjczIDUxMy44NjUgMTE2LjY3NyA1MTIuNDY4IDExNS42ODNDNTExLjI3IDExNC40OSA1MTAuNjcgMTEzLjA5OCA1MTAuNjcgMTExLjExQzUxMC42NyAxMDguMTI4IDUxMS42NjkgMTA1LjM0NCA1MTMuNDY3IDEwMi43NkM1MTcuMjYgMTAzLjk1MyA1MjEuNDU1IDEwNC4zNSA1MjYuMDQ0IDEwNC4zNUM1MzUuMjMgMTA0LjM1IDU0Mi42MTcgMTAyLjE2MyA1NDcuNjExIDk3Ljc4OUM1NTIuODAxIDkzLjIxNyA1NTUuMzk2IDg3LjI1MiA1NTUuMzk2IDgwLjA5NEM1NTUuMzk2IDc1LjEyNCA1NTQuMzk3IDcwLjk0OSA1NTIuMjA0IDY3LjM3SDU2Ni43NzlWNTYuODMzTDU2NC41ODIgNTUuMjQyTDU0Ny44MSA2Mi4yMDFaTTUxMS4wNzEgMTMyLjc4MUM1MTQuMDY1IDEzMy4zNzggNTE3LjI2IDEzMy43NzUgNTIxLjA1MyAxMzMuNzc1SDUzNy44MjVDNTQyLjYxNyAxMzMuNzc1IDU0Ni4wMTIgMTM0Ljc2OSA1NDguMDA5IDEzNi43NThDNTUwLjAwNyAxMzguNzQ2IDU1MS4wMDYgMTQxLjEzMiA1NTEuMDA2IDE0My45MTVDNTUxLjAwNiAxNDcuNjkzIDU0OS4wMDggMTUwLjg3NCA1NDQuODE0IDE1My40NThDNTQwLjgyMiAxNTYuMDQzIDUzNC44MzIgMTU3LjQzNSA1MjYuODQ0IDE1Ny40MzVDNTIwLjQ1NiAxNTcuNDM1IDUxNS42NjQgMTU2LjQ0MSA1MTIuMjY5IDE1NC4yNTRDNTA4Ljg3NSAxNTIuMDY3IDUwNy4wNzYgMTQ4LjY4NyA1MDcuMDc2IDE0NC4xMTRDNTA2Ljg3NyAxNDAuMzM2IDUwOC4yNzQgMTM2LjU1OSA1MTEuMDcxIDEzMi43ODFaTTUzNS42MzIgOTMuMjE3QzUzMy40MzUgOTYuNTk2IDUzMC4yMzkgOTguMTg3IDUyNi4wNDQgOTguMTg3QzUyMS44NTMgOTguMTg3IDUxOC44NTYgOTYuNTk2IDUxNi44NjIgOTMuNDE1QzUxNC42NjUgOTAuMjM0IDUxMy42NjYgODUuODYgNTEzLjY2NiA4MC40OTJDNTEzLjY2NiA3NS4xMjQgNTE0Ljg2NCA3MC43NSA1MTcuMDYxIDY3LjU2OUM1MTkuNDU3IDY0LjE4OSA1MjIuNjUzIDYyLjU5OCA1MjYuNjQ1IDYyLjU5OEM1MzAuNjM3IDYyLjU5OCA1MzMuODMzIDY0LjE4OSA1MzUuODMxIDY3LjM3QzUzOC4wMjggNzAuNTUxIDUzOS4yMjYgNzQuNzI2IDUzOS4yMjYgODAuMDk0QzUzOS4wMjMgODUuNDYzIDUzOC4wMjggOTAuMDM1IDUzNS42MzIgOTMuMjE3WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik02NDcuNjI1IDExMC4xMDNWODIuODY1QzY0Ny42MjUgNzMuNTIgNjQ1LjgzIDY2Ljc2IDY0Mi4yMzYgNjIuMzg3QzYzOC42NDIgNTguMDEzIDYzMy40NDggNTUuODI1IDYyNy4wNiA1NS44MjVDNjE3LjY3NiA1NS44MjUgNjA4Ljg5MiA2MC4yIDYwMS4zMDIgNjkuMTQ3VjQyLjMwNkw2MDEuOTAzIDIxLjAzMkw1OTkuNzA2IDE5LjY0MUw1NzIuNzUgMjYuNFYzMi4zNjVMNTgzLjczMSAzMy45NTZWMTA5LjkwNEM1ODMuNzMxIDExNC4yNzggNTgzLjczMSAxMTguMjU0IDU4My41MzIgMTIyLjAzMkw1NzMuNTUgMTI0LjAyVjEzMC4xODRINjEwLjg4NlYxMjQuMDJMNjAxLjkwMyAxMjIuMjMxQzYwMS43IDExOC40NTMgNjAxLjcgMTE0LjI3OCA2MDEuNyAxMTAuMTAzVjc3LjI5OEM2MDcuNjk0IDcxLjUzMiA2MTMuNjg0IDY4Ljc0OSA2MTkuMjcyIDY4Ljc0OUM2MjMuMDY4IDY4Ljc0OSA2MjUuODYyIDY5Ljk0MiA2MjcuMjYgNzIuMTI5QzYyOC44NTYgNzQuMzE2IDYyOS42NTUgNzguNDkxIDYyOS42NTUgODQuMjU3VjExMC4xMDNDNjI5LjY1NSAxMTQuMjc4IDYyOS42NTUgMTE4LjI1NCA2MjkuNDU2IDEyMi4wMzJMNjE5Ljg3MyAxMjQuMDJWMTMwLjE4NEg2NTcuMDFWMTI0LjAyTDY0Ny44MjggMTIyLjIzMUM2NDcuNjI1IDExOC40NTMgNjQ3LjYyNSAxMTQuNDc3IDY0Ny42MjUgMTEwLjEwM1oiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMzc2LjI5NyAzMC4zODNIMzQyLjk1MVYzNy4zNDJMMzU1LjMzIDM5LjEzMUwzMzYuOTYxIDEwNC45NEwzMTYuNzk0IDM4LjkzMkwzMzAuOTcxIDM3LjM0MlYzMC4zODNIMjg3Ljg0MlYzNy4zNDJMMzAxLjAyIDM4LjkzMkwyODAuMjU0IDEwNC4xNDVMMjYzLjA4MiAzOC45MzJMMjc1LjY2MiAzNy4zNDJWMzAuMzgzSDIzMS43MzRWMzcuMzQyTDI0Mi43MTYgMzguNTM0TDI2OS44NzEgMTMwLjU4N0gyODAuMjU0TDMwMy4wMTcgNTcuMjIzTDMyNi45NzcgMTMwLjU4N0gzMzcuMzZMMzYzLjUxNyAzOS4xMzFMMzc1LjY5NiAzNy4xNDNWMzAuMzgzSDM3Ni4yOTdaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTQ2Ny4xMjggNDEuOTE4QzQ3MC4zMjEgNDEuOTE4IDQ3My4xMTggNDAuOTI0IDQ3NS4xMTIgMzguOTM1QzQ3Ny4zMDkgMzYuOTQ3IDQ3OC41MDcgMzQuMzYzIDQ3OC41MDcgMzEuMTgyQzQ3OC41MDcgMjggNDc3LjMwOSAyNS40MTYgNDc1LjExMiAyMy40MjhDNDcyLjkxNiAyMS40MzkgNDcwLjMyMSAyMC40NDUgNDY3LjEyOCAyMC40NDVDNDYzLjkzMyAyMC40NDUgNDYxLjEzNSAyMS40MzkgNDU4Ljk0MiAyMy40MjhDNDU2Ljc0NSAyNS40MTYgNDU1LjU0NyAyOCA0NTUuNTQ3IDMxLjE4MkM0NTUuNTQ3IDM0LjM2MyA0NTYuNzQ1IDM2Ljk0NyA0NTguOTQyIDM4LjkzNUM0NjEuMTM1IDQwLjkyNCA0NjMuOTMzIDQxLjkxOCA0NjcuMTI4IDQxLjkxOFoiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNNDc2LjExNCAxMDkuOTA2Vjc4LjQ5M0w0NzYuNTEyIDU3LjIyTDQ3NC4xMTYgNTUuNjI5TDQ0Ni45NjEgNjUuMTcyVjcwLjkzOEw0NTcuNzQ2IDcyLjMzQzQ1Ny45NDUgNzUuMzEyIDQ1OC4xNDQgNzguMjk0IDQ1OC4xNDQgODEuMDc4QzQ1OC4zNDMgODMuODYxIDQ1OC4zNDMgODcuMjQxIDQ1OC4zNDMgOTEuMjE4VjEwOS43MDhDNDU4LjM0MyAxMTQuMDgyIDQ1OC4zNDMgMTE4LjA1OCA0NTguMTQ0IDEyMS44MzZMNDQ4LjE1OSAxMjMuODI0VjEyOS45ODdINDg1LjY5OFYxMjMuODI0TDQ3Ni41MTIgMTIyLjAzNEM0NzYuMzEzIDExOC4yNTcgNDc2LjExNCAxMTQuMjggNDc2LjExNCAxMDkuOTA2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xMTQ0LjIzIDEyMi4yNDRDMTE0MS4yMyAxMjIuMjQ0IDExMzkuODMgMTIwLjA1NyAxMTM5LjgzIDExNS40ODRWODIuNjhDMTEzOS44MyA3Mi45MzggMTEzNy44MyA2NS43OCAxMTMzLjg0IDYxLjgwNEMxMTI5Ljg1IDU3LjYyOSAxMTIzLjQ2IDU1LjQ0MSAxMTE0LjY4IDU1LjQ0MUMxMTA1Ljg5IDU1LjQ0MSAxMDk4LjEgNTcuMjMxIDEwOTIuNTEgNjAuODFDMTA4Ni45MiA2NC4zODggMTA4My43MyA2OS4xNiAxMDgyLjkzIDc1LjMyM0MxMDgzLjczIDc5Ljg5NiAxMDg2LjUyIDgyLjA4MyAxMDkxLjMxIDgyLjA4M0MxMDkzLjkxIDgyLjA4MyAxMDk1LjkxIDgxLjI4OCAxMDk3LjcgNzkuNDk5QzEwOTkuNSA3Ny43MDkgMTEwMC41IDc1LjEyNCAxMTAwLjkgNzEuNTQ2TDExMDIuNyA2My4xOTVDMTEwMy44OSA2Mi45OTYgMTEwNC44OSA2Mi43OTggMTEwNS44OSA2Mi43OThDMTEwNy4wOSA2Mi41OTkgMTEwOC4wOCA2Mi41OTkgMTEwOC44OCA2Mi41OTlDMTExMy44OCA2Mi41OTkgMTExNy4yNyA2My43OTIgMTExOS4wNyA2Ni4zNzZDMTEyMS4wNiA2OC43NjIgMTEyMi4wNiA3My41MzQgMTEyMi4wNiA4MC40OTNWODQuNjY4QzExMTkuNDcgODUuNDYzIDExMTYuODcgODYuMDU5IDExMTQuMjcgODYuODU1QzExMTEuNjggODcuNjUgMTEwOS40OCA4OC4yNDYgMTEwNy40OSA4OS4wNDJDMTEwMC4zIDkxLjQyOCAxMDk0LjcxIDkzLjYxNSAxMDkwLjcyIDk2LjE5OUMxMDg2LjkyIDk4LjU4NSAxMDg0LjEzIDEwMS4xNyAxMDgyLjczIDEwMy45NTNDMTA4MS4xMyAxMDYuNzM2IDEwODAuNTMgMTA5LjcxOSAxMDgwLjUzIDExMi45QzEwODAuNTMgMTE5LjA2MyAxMDgyLjUzIDEyMy44MzUgMTA4Ni4zMiAxMjcuMDE2QzEwOTAuMzEgMTMwLjE5NyAxMDk1LjExIDEzMS43ODggMTEwMC43IDEzMS43ODhDMTEwNS40OSAxMzEuNzg4IDExMDkuNDggMTMwLjc5NCAxMTEyLjQ4IDEyOS4wMDRDMTExNS40NyAxMjcuMDE2IDExMTguODcgMTI0LjAzNCAxMTIyLjY2IDEyMC4yNTZDMTEyMy42NiAxMjMuODM1IDExMjUuMjYgMTI2LjYxOCAxMTI3Ljg1IDEyOC42MDZDMTEzMC40NSAxMzAuNTk1IDExMzMuNjQgMTMxLjU4OSAxMTM3LjY0IDEzMS41ODlDMTE0MS4yMyAxMzEuNTg5IDExNDQuMjMgMTMwLjc5NCAxMTQ2LjYyIDEyOS40MDJDMTE0OS4yMiAxMjcuODExIDExNTEuMjIgMTI1LjQyNSAxMTUzLjIxIDEyMi4wNDVMMTE0OS44MiAxMTkuMDYzQzExNDcuODIgMTIxLjA1MSAxMTQ2LjAyIDEyMi4yNDQgMTE0NC4yMyAxMjIuMjQ0Wk0xMTIxLjg2IDExNC40OUMxMTE4LjI3IDExNy4wNzUgMTExNS40NyAxMTguNjY2IDExMTMuODggMTE5LjQ2MUMxMTEyLjA4IDEyMC4yNTYgMTExMC40OCAxMjAuNjU0IDExMDguNjkgMTIwLjY1NEMxMTA1LjY5IDEyMC42NTQgMTEwMy4wOSAxMTkuODU5IDExMDAuOSAxMTguMDY5QzEwOTguOSAxMTYuMjggMTA5Ny45IDExMy4yOTggMTA5Ny45IDEwOS41MkMxMDk3LjkgMTA2LjUzOCAxMDk4LjkgMTAzLjc1NCAxMTAwLjcgMTAxLjE3QzExMDIuNyA5OC41ODUgMTEwNi4wOSA5Ni4xOTkgMTExMS4wOCA5NC4yMTFDMTExMi40OCA5My42MTUgMTExMy44OCA5My4yMTcgMTExNS44NyA5Mi42MkMxMTE3Ljg3IDkyLjAyNCAxMTE5Ljg3IDkxLjQyOCAxMTIxLjg2IDkwLjYzMlYxMTQuNDlaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTExOTQuOTIgODUuODYxTDExODguOTMgODQuMDcxQzExODMuNzMgODIuMjgyIDExODAuMzQgODAuNjkxIDExNzguMzQgNzkuMTAxQzExNzYuNTQgNzcuMzExIDExNzUuNTQgNzUuMTI0IDExNzUuNTQgNzIuNTRDMTE3NS41NCA2OS41NTcgMTE3Ni43NCA2Ny4zNyAxMTc4Ljk0IDY1LjU4MUMxMTgxLjE0IDYzLjc5MiAxMTg0LjMzIDYyLjk5NiAxMTg4LjMyIDYyLjk5NkMxMTkxLjcyIDYyLjk5NiAxMTk0LjkyIDYzLjU5MyAxMTk3LjcxIDY0Ljc4NkwxMjAwLjUxIDc3LjUxSDEyMTAuNDlMMTIxMS4yOSA2MS42MDVDMTIwNy42OSA1OS42MTYgMTIwNC4xIDU4LjAyNiAxMjAwLjUxIDU3LjAzMkMxMTk2LjkxIDU1LjgzOSAxMTkzLjEyIDU1LjQ0MSAxMTg4LjczIDU1LjQ0MUMxMTgyLjUzIDU1LjQ0MSAxMTc3LjM0IDU2LjQzNSAxMTcyLjk1IDU4LjYyMkMxMTY4Ljc2IDYwLjYxMSAxMTY1LjU2IDYzLjM5NCAxMTYzLjM3IDY2Ljk3M0MxMTYxLjE3IDcwLjM1MyAxMTU5Ljk3IDc0LjEzIDExNTkuOTcgNzguNTA0QzExNTkuOTcgODMuODczIDExNjEuNTcgODguMjQ2IDExNjQuNzYgOTEuODI1QzExNjguMTYgOTUuNDA0IDExNzIuNTUgOTcuOTg5IDExNzguMTQgOTkuNzc4TDExODUuNzMgMTAyLjM2M0MxMTkwLjUyIDEwMy45NTMgMTE5My45MiAxMDUuNzQzIDExOTUuOTEgMTA3LjUzMkMxMTk3LjkxIDEwOS4zMjEgMTE5OC45MSAxMTEuNTA4IDExOTguOTEgMTE0LjI5MUMxMTk4LjkxIDExNy40NzMgMTE5Ny43MSAxMjAuMDU3IDExOTUuMTEgMTIxLjg0N0MxMTkyLjUyIDEyMy42MzYgMTE4OC43MyAxMjQuNjMgMTE4My41MyAxMjQuNjNDMTE3OS4zNCAxMjQuNjMgMTE3NS4zNSAxMjMuODM1IDExNzEuNzUgMTIyLjQ0M0wxMTY4Ljk2IDEwOC41MjZIMTE1OC43N0wxMTU4Ljk3IDEyNi4wMjJDMTE2Mi43NyAxMjguMjA5IDExNjYuNTYgMTI5LjYwMSAxMTcwLjU1IDEzMC41OTVDMTE3NC41NSAxMzEuNzg4IDExNzguNzQgMTMyLjE4NSAxMTgzLjMzIDEzMi4xODVDMTE5My41MiAxMzIuMTg1IDEyMDEuMyAxMjkuOTk4IDEyMDYuNyAxMjUuNjI0QzEyMTIuMjggMTIxLjI1IDEyMTUuMDggMTE1LjY4MyAxMjE1LjA4IDEwOC45MjRDMTIxNS4wOCAxMDMuNzU0IDEyMTMuNDkgOTkuMTgxIDEyMTAuNDkgOTUuNjAzQzEyMDcuNDkgOTEuNDI4IDEyMDIuMyA4OC4yNDYgMTE5NC45MiA4NS44NjFaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTEyOTIuMTcgODUuNjYyQzEyOTIuMTcgNzkuNDk5IDEyOTAuOTcgNzQuMTMgMTI4OC4zNyA2OS43NTZDMTI4NS45OCA2NS4xODQgMTI4Mi41OCA2MS44MDQgMTI3OC4xOSA1OS4yMTlDMTI3My44IDU2LjYzNCAxMjY4LjYgNTUuNDQxIDEyNjIuNjEgNTUuNDQxQzEyNTYuMjMgNTUuNDQxIDEyNTAuMjQgNTcuMDMyIDEyNDQuNjQgNjAuMDE0QzEyMzkuMDUgNjIuOTk2IDEyMzQuNDYgNjcuMzcgMTIzMS4wNyA3My4zMzVDMTIyNy42NyA3OS4xMDEgMTIyNS44OCA4NS44NjEgMTIyNS44OCA5NC4wMTJDMTIyNS44OCAxMDEuOTY1IDEyMjcuNDcgMTA4LjUyNiAxMjMwLjQ3IDExNC4yOTFDMTIzMy40NiAxMTkuODU5IDEyMzcuNjYgMTI0LjIzMyAxMjQzLjA0IDEyNy4yMTVDMTI0OC40NCAxMzAuMTk3IDEyNTQuNjMgMTMxLjc4OCAxMjYxLjYyIDEzMS43ODhDMTI2OC42IDEzMS43ODggMTI3NC43OSAxMzAuMTk3IDEyNzkuNzkgMTI3LjIxNUMxMjg0Ljk4IDEyNC4wMzQgMTI4OC45NyAxMTkuODU5IDEyOTEuOTcgMTE0LjI5MUwxMjg3LjU3IDExMC4zMTVDMTI4NC45OCAxMTMuMDk5IDEyODIuMTggMTE1LjQ4NSAxMjc5LjE5IDExNy4yNzRDMTI3Ni4xOSAxMTkuMDYzIDEyNzIuNCAxMTkuODU5IDEyNjguMDEgMTE5Ljg1OUMxMjYxLjYyIDExOS44NTkgMTI1Ni40MyAxMTcuNjcxIDEyNTIuMDMgMTEzLjI5OEMxMjQ3Ljg0IDEwOC45MjQgMTI0NS42NCAxMDIuNTYxIDEyNDUuMjQgOTMuODEzSDEyOTEuNTdDMTI5MS45NyA5MS42MjYgMTI5Mi4xNyA4OC44NDMgMTI5Mi4xNyA4NS42NjJaTTEyNzMuMiA4NC40NjlDMTI3MiA4Ni4wNTkgMTI2OS42IDg2LjY1NiAxMjY2LjAxIDg2LjY1NkgxMjQ1LjI0QzEyNDUuNjQgODAuNjkxIDEyNDYuNjQgNzUuOTIgMTI0OC4yNCA3Mi4zNDFDMTI1MC4wMyA2OC43NjIgMTI1Mi4wMyA2Ni4zNzYgMTI1NC4yMyA2NC43ODZDMTI1Ni42MiA2My4xOTUgMTI1OS4wMiA2Mi40IDEyNjEuNDIgNjIuNEMxMjY1LjIxIDYyLjQgMTI2OC40IDYzLjc5MiAxMjcxIDY2Ljc3NEMxMjczLjU5IDY5Ljc1NiAxMjc1IDczLjUzNCAxMjc1IDc4LjEwN0MxMjc1IDgwLjg5IDEyNzQuMzkgODMuMDc3IDEyNzMuMiA4NC40NjlaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTY5OS4xNTYgMTIyLjQ0MkM2OTYuNzYgMTIyLjQ0MiA2OTQuNzYyIDEyMS42NDYgNjkzLjE2NiAxMTkuODU3QzY5MS43NjkgMTE4LjA2OCA2OTAuOTY5IDExNS40ODMgNjkwLjk2OSAxMTEuNzA2VjY3LjM2OUg3MDkuMzQxVjU4LjAyNEg2OTEuMTY4TDY5MS43NjkgMzcuMzQ4SDY3OS41ODdMNjczLjggNTguMDI0TDY2MS42MTcgNTkuNjE1VjY3LjM2OUg2NzIuODAxVjk5LjM3OUM2NzIuODAxIDEwMi4zNjEgNjcyLjgwMSAxMDQuNzQ3IDY3Mi41OTggMTA2LjkzNFYxMTMuNDk1QzY3Mi41OTggMTIwLjA1NiA2NzQuMzk3IDEyNS4wMjYgNjc3Ljc5MiAxMjguMDA4QzY4MS4xODYgMTMwLjk5MSA2ODUuOTc4IDEzMi41ODEgNjkxLjk2OCAxMzIuNTgxQzY5Ni43NiAxMzIuNTgxIDcwMC43NTIgMTMxLjc4NiA3MDQuMTQ3IDEyOS45OTdDNzA3LjU0MiAxMjguMjA3IDcxMC4xMzcgMTI1LjgyMiA3MTEuOTM2IDEyMi42NDFMNzA4LjM0MiAxMTguODYzQzcwNS4xNDYgMTIxLjA1IDcwMS45NSAxMjIuMjQzIDY5OS4xNTYgMTIyLjQ0MloiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMTM1NS42NiA5NS4wMDZDMTM1Mi40NiA5MS4yMjggMTM0Ny4yNyA4OC4yNDYgMTMzOS44OCA4NS42NjFMMTMzMy44OSA4My44NzJDMTMyOC43IDgyLjA4MyAxMzI1LjMxIDgwLjQ5MiAxMzIzLjMxIDc4LjkwMUMxMzIxLjUxIDc3LjExMiAxMzIwLjUxIDc0LjkyNSAxMzIwLjUxIDcyLjM0QzEzMjAuNTEgNjkuMzU4IDEzMjEuNzEgNjcuMTcxIDEzMjMuOTEgNjUuMzgyQzEzMjYuMTEgNjMuNTkzIDEzMjkuMyA2Mi43OTcgMTMzMy4yOSA2Mi43OTdDMTMzNi42OSA2Mi43OTcgMTMzOS44OCA2My4zOTQgMTM0Mi42OCA2NC41ODZMMTM0NS40NyA3Ny4zMTFIMTM1NS40NkwxMzU2LjI1IDYxLjQwNUMxMzUyLjY2IDU5LjQxNyAxMzQ5LjA3IDU3LjgyNyAxMzQ1LjQ3IDU2LjgzM0MxMzQxLjg4IDU1LjY0IDEzMzguMDkgNTUuMjQyIDEzMzMuNjkgNTUuMjQyQzEzMjcuNSA1NS4yNDIgMTMyMi4zMSA1Ni4yMzYgMTMxNy45MiA1OC40MjNDMTMxMy43MiA2MC40MTEgMTMxMC41MyA2My4xOTUgMTMwOC4zNCA2Ni43NzRDMTMwNi4xNCA3MC4xNTQgMTMwNC45NCA3My45MzEgMTMwNC45NCA3OC4zMDVDMTMwNC45NCA4My42NzMgMTMwNi41NCA4OC4wNDcgMTMwOS43MyA5MS42MjZDMTMxMy4xMyA5NS4yMDUgMTMxNy41MiA5Ny43ODkgMTMyMy4xMSA5OS41NzlMMTMzMC43IDEwMi4xNjNDMTMzNS40OSAxMDMuNzU0IDEzMzguODkgMTA1LjU0MyAxMzQwLjg4IDEwNy4zMzNDMTM0Mi44OCAxMDkuMTIyIDEzNDMuODggMTExLjMwOSAxMzQzLjg4IDExNC4wOTJDMTM0My44OCAxMTcuMjczIDEzNDIuNjggMTE5Ljg1OCAxMzQwLjA4IDEyMS42NDdDMTMzNy40OCAxMjMuNDM3IDEzMzMuNjkgMTI0LjQzMSAxMzI4LjUgMTI0LjQzMUMxMzI0LjMxIDEyNC40MzEgMTMyMC4zMSAxMjMuNjM1IDEzMTYuNzIgMTIyLjI0NEwxMzEzLjkzIDEwOC4zMjdIMTMwMy43NEwxMzAzLjk0IDEyNS44MjNDMTMwNy43MyAxMjguMDEgMTMxMS41MyAxMjkuNDAxIDEzMTUuNTIgMTMwLjM5NUMxMzE5LjUxIDEzMS41ODggMTMyMy43MSAxMzEuOTg2IDEzMjguMyAxMzEuOTg2QzEzMzguNDggMTMxLjk4NiAxMzQ2LjI3IDEyOS43OTkgMTM1MS42NiAxMjUuNDI1QzEzNTcuMjUgMTIxLjA1MSAxMzYwLjA1IDExNS40ODQgMTM2MC4wNSAxMDguNzI0QzEzNjAuNDUgMTAzLjM1NiAxMzU4Ljg1IDk4Ljc4MyAxMzU1LjY2IDk1LjAwNloiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNNzU0LjI1OSA4Ni40NTFMNzQ4LjI2OSA4NC42NjJDNzQzLjA3NSA4Mi44NzIgNzM5LjY4MSA4MS4yODIgNzM3LjY4NiA3OS42OTFDNzM1Ljg4OCA3Ny45MDIgNzM0Ljg4OSA3NS43MTUgNzM0Ljg4OSA3My4xM0M3MzQuODg5IDcwLjE0OCA3MzYuMDg3IDY3Ljk2MSA3MzguMjg0IDY2LjE3MkM3NDAuNDggNjQuMzgyIDc0My42NzYgNjMuNTg3IDc0Ny42NjggNjMuNTg3Qzc1MS4wNjMgNjMuNTg3IDc1NC4yNTkgNjQuMTgzIDc1Ny4wNTMgNjUuMzc2TDc1OS44NDcgNzguMUg3NjkuODMzTDc3MC42MzIgNjIuMzk0Qzc2Ny4wMzUgNjAuNDA2IDc2My40NDEgNTguODE1IDc1OS44NDcgNTcuODIxQzc1Ni4yNTMgNTYuNjI4IDc1Mi40NiA1Ni4yMyA3NDguMDY2IDU2LjIzQzc0MS44NzggNTYuMjMgNzM2LjY4OCA1Ny4yMjUgNzMyLjI5NCA1OS40MTJDNzI4LjEwMyA2MS40IDcyNC45MDcgNjQuMTgzIDcyMi43MSA2Ny43NjJDNzIwLjUxMyA3MS4xNDIgNzE5LjMxNSA3NC45MTkgNzE5LjMxNSA3OS4yOTNDNzE5LjMxNSA4NC42NjIgNzIwLjkxMSA4OS4wMzYgNzI0LjEwNyA5Mi42MTRDNzI3LjUwMiA5Ni4xOTMgNzMxLjg5NiA5OC43NzggNzM3LjQ4NCAxMDAuNTY3TDc0NS4wNzMgMTAzLjE1MkM3NDkuODY1IDEwNC43NDIgNzUzLjI2IDEwNi41MzIgNzU1LjI1OCAxMDguMzIxQzc1Ny4yNTIgMTEwLjExIDc1OC4yNTEgMTEyLjI5NyA3NTguMjUxIDExNS4wODFDNzU4LjI1MSAxMTguMjYyIDc1Ny4wNTMgMTIwLjg0NyA3NTQuNDU4IDEyMi42MzZDNzUxLjg2MyAxMjQuNDI1IDc0OC4wNjYgMTI1LjQxOSA3NDIuODc2IDEyNS40MTlDNzM4LjY4MiAxMjUuNDE5IDczNC42OSAxMjQuNjI0IDczMS4wOTYgMTIzLjIzMkw3MjguMzAyIDEwOS4zMTVINzE4LjExN0w3MTguMzE2IDEyNi44MTFDNzIyLjEwOSAxMjguOTk4IDcyNS45MDYgMTMwLjM5IDcyOS44OTggMTMxLjM4NEM3MzMuODkgMTMyLjU3NyA3MzguMDg1IDEzMi45NzQgNzQyLjY3NyAxMzIuOTc0Qzc1Mi44NTggMTMyLjk3NCA3NjAuNjQ3IDEzMC43ODcgNzY2LjA0IDEyNi40MTNDNzcxLjYyOCAxMjIuMDM5IDc3NC40MjUgMTE2LjQ3MiA3NzQuNDI1IDEwOS43MTNDNzc0LjQyNSAxMDQuNTQzIDc3Mi44MjYgOTkuOTcxIDc2OS44MzMgOTYuMzkyQzc2Ni44MzYgOTIuMDE4IDc2MS42NDYgODguODM3IDc1NC4yNTkgODYuNDUxWiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xMDYxLjE2IDEwOS4zMTdWNzcuOTAzTDEwNjEuNTYgNTYuNjNMMTA1OS4xNiA1NS4wMzlMMTAzMi4wMSA2NC41ODNWNzAuMzQ4TDEwNDIuNzkgNzEuNzRDMTA0Mi45OSA3NC43MjIgMTA0Mi45OSA3Ny43MDQgMTA0Mi45OSA4MC40ODhDMTA0My4xOSA4My4yNzIgMTA0My4xOSA4Ni42NTEgMTA0My4xOSA5MC42MjhWMTA5LjExOEMxMDQzLjE5IDExMy40OTIgMTA0My4xOSAxMTcuNDY4IDEwNDIuOTkgMTIxLjI0NkwxMDMzLjAxIDEyMy4yMzRWMTI5LjM5N0gxMDcwLjU0VjEyMy4yMzRMMTA2MS4zNiAxMjEuNDQ1QzEwNjEuMTYgMTE3LjY2NyAxMDYxLjE2IDExMy42OTEgMTA2MS4xNiAxMDkuMzE3WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik04NzMuODY3IDY5Ljk0N0w4ODUuNjQ4IDcxLjkzNUM4ODQuNDUgNzcuMzAzIDg4My4wNTMgODIuMjc0IDg4MS4yNTQgODYuODQ2Qzg3OS40NTkgOTEuMjIgODc3LjQ2MSA5NS41OTQgODc0LjY2NyAxMDAuMTY3Qzg3Mi4wNjggOTcuNTgyIDg2OS42NzIgOTQuOTk4IDg2Ny4wNzcgOTIuMjE0Qzg2NC40ODIgODkuNDMxIDg2MS44ODcgODYuNDQ5IDg1OC44OSA4My4yNjdDODU2LjI5NSA4MC40ODQgODU0LjA5OSA3OC4wOTggODUyLjEwMSA3Ni4xMUM4NTAuMTA3IDczLjkyMyA4NDguNTA3IDcyLjEzNCA4NDcuMTEgNzAuNTQzQzg1NC44OTggNjYuNzY2IDg2MC40OSA2Mi45ODggODY0LjI4MyA1OS4wMTJDODY3Ljg3NyA1NS4wMzUgODY5LjY3MiA1MC40NjIgODY5LjY3MiA0NS4yOTNDODY5LjY3MiAzOS41MjcgODY3LjQ3NSAzNC45NTUgODYzLjI4NCAzMS4zNzZDODU5LjA4OSAyNy43OTcgODUyLjkgMjYuMDA4IDg0NC45MTMgMjYuMDA4QzgzNi45MjkgMjYuMDA4IDgzMC43MzYgMjcuOTk2IDgyNS45NDQgMzEuOTcyQzgyMC45NTMgMzUuOTQ5IDgxOC41NTcgNDEuNTE2IDgxOC41NTcgNDguNDc0QzgxOC41NTcgNTIuMjUyIDgxOS4zNTcgNTYuMjI4IDgyMC43NTQgNjAuMDA2QzgyMi4xNTEgNjMuOTgyIDgyNC43NDYgNjcuOTU5IDgyOC4zNCA3Mi4zMzJDODI4LjUzOSA3Mi41MzEgODI4Ljc0MiA3Mi41MzEgODI4Ljc0MiA3Mi43M0M4MjguOTQxIDcyLjkyOSA4MjguOTQxIDcyLjkyOSA4MjkuMTQgNzMuMTI4QzgyMS4zNTIgNzYuOTA1IDgxNS41NjEgODEuMDggODExLjc2OCA4Ni4wNTFDODA3Ljk3NSA5MC44MjIgODA2LjE4IDk2LjM5IDgwNi4xOCAxMDIuNzUyQzgwNi4xOCAxMDcuNzIyIDgwNy4zNzggMTEyLjA5NiA4MDkuOTczIDExNi4yNzFDODEyLjU2OCAxMjAuMjQ4IDgxNi4xNjIgMTIzLjYyOCA4MjAuOTUzIDEyNi4wMTRDODI1Ljc0NSAxMjguMzk5IDgzMS4zMzcgMTI5LjU5MiA4MzcuNzI1IDEyOS41OTJDODQ0LjkxMyAxMjkuNTkyIDg1MC45MDMgMTI4LjM5OSA4NTUuNjk1IDEyNi4yMTJDODYwLjQ5IDEyMy44MjYgODY0LjQ4MiAxMjEuMDQzIDg2Ny42NzggMTE3Ljg2MkM4NjguNDc0IDExOC42NTcgODY5LjA3NSAxMTkuMjU0IDg2OS44NzEgMTIwLjA0OUM4NzAuNjcxIDEyMC44NDQgODcxLjQ3MSAxMjEuNDQxIDg3Mi4wNjggMTIyLjIzNkM4NzUuMDY1IDEyNS4wMTkgODc4LjA1OCAxMjcuMDA4IDg4MS4wNTUgMTI4LjAwMUM4ODQuMDQ4IDEyOS4xOTUgODg3LjY0NSAxMjkuNTkyIDg5Mi4wMzUgMTI5LjU5MkM4OTQuMjMyIDEyOS41OTIgODk2LjAzMSAxMjkuMzkzIDg5OC4wMjUgMTI5LjE5NUM5MDAuMDIzIDEyOC45OTYgOTAyLjIyIDEyOC41OTggOTA1LjIxMyAxMjcuODAzTDkwNi4yMTIgMTE5LjQ1M0w4OTEuNjM3IDExNi44NjhDODg5LjQ0IDExNC40ODIgODg3LjQ0MyAxMTIuNDk0IDg4NS40NDggMTEwLjMwN0M4ODMuNDUxIDEwOC4zMTkgODgxLjY1MiAxMDYuMzMgODc5Ljg1NyAxMDQuMzQyQzg4My40NTEgOTkuMTczIDg4Ni40NDQgOTQuMDA0IDg4OC44NDMgODguODM0Qzg5MS40MzggODMuNjY1IDg5My42MzUgNzcuNzAxIDg5NS40MyA3MS4xNEw5MDYuNDExIDY5LjM1VjYyLjc4OUg4NzQuNDY0TDg3My44NjcgNjkuOTQ3Wk04MzYuMzI4IDM1LjM1MkM4MzguNzI0IDMyLjk2NiA4NDEuNTE4IDMxLjc3NCA4NDQuOTEzIDMxLjc3NEM4NDguMzA4IDMxLjc3NCA4NTEuMTA1IDMyLjk2NiA4NTMuMjk5IDM1LjE1M0M4NTUuNDk2IDM3LjM0IDg1Ni42OTMgNDAuMzIzIDg1Ni42OTMgNDQuMjk5Qzg1Ni42OTMgNDguMDc3IDg1NS40OTYgNTEuNjU1IDg1My4yOTkgNTUuMjM0Qzg1MC45MDMgNTguODEzIDg0Ny43MTEgNjIuMzkxIDg0My43MTUgNjUuOTdDODQyLjkxOSA2NC45NzYgODQyLjExOSA2My45ODIgODQxLjUxOCA2My4xODdDODQwLjcyMiA2Mi4xOTMgODQwLjEyMSA2MS4zOTcgODM5LjMyNSA2MC40MDRDODM2LjkyOSA1Ny4yMjIgODM1LjMyOSA1NC4yNCA4MzQuNTMzIDUxLjg1NEM4MzMuNzMzIDQ5LjI3IDgzMy4zMzUgNDYuODg0IDgzMy4zMzUgNDQuNDk4QzgzMi45MzMgNDAuOTE5IDgzNC4xMzEgMzcuOTM3IDgzNi4zMjggMzUuMzUyWk04NDQuNzE0IDExOS4wNTVDODQwLjMyIDExOS4wNTUgODM2LjUyNyAxMTguMDYxIDgzMy4xMzIgMTE2LjI3MUM4MjkuOTQgMTE0LjI4MyA4MjcuMzQxIDExMS44OTcgODI1LjU0NiAxMDguNTE4QzgyMy43NDcgMTA1LjMzNiA4MjIuNzUyIDEwMS43NTggODIyLjc1MiA5Ny45OEM4MjIuNzUyIDk0LjQwMSA4MjMuNTQ4IDkxLjAyMSA4MjQuOTQ1IDg3LjQ0M0M4MjYuMzQ2IDgzLjg2NCA4MjguOTQxIDgwLjY4MyA4MzIuNzM0IDc3Ljg5OUM4MzQuNzMyIDgwLjI4NSA4MzYuOTI5IDgzLjA2OSA4MzkuMzI1IDg2LjA1MUM4NDEuOTIgODkuMDMzIDg0NC45MTMgOTIuNjEyIDg0OC4zMDggOTYuNzg3Qzg1MC41MDUgOTkuMzcyIDg1Mi43MDEgMTAyLjE1NSA4NTUuMDk3IDEwNC45MzlDODU3LjQ5MyAxMDcuNzIyIDg2MC4wODggMTEwLjUwNiA4NjIuNjgzIDExMy4yODlDODU3LjY5MiAxMTcuMDY2IDg1MS43MDMgMTE4Ljg1NiA4NDQuNzE0IDExOS4wNTVaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTk5My4yNyA3Ni45MTNDMTAwMi4yNSA3NS4xMjMgMTAwOC42NCA3Mi4zNCAxMDEyLjIzIDY3Ljk2NkMxMDE1LjgzIDYzLjU5MiAxMDE3LjYzIDU4LjgyMSAxMDE3LjYzIDUzLjY1MUMxMDE3LjYzIDQ2LjY5MiAxMDE0LjgzIDQwLjkyNyAxMDA5LjI0IDM2LjU1M0MxMDAzLjY1IDMxLjk4IDk5NS4wNiAyOS43OTMgOTgzLjQ4IDI5Ljc5M0g5MzcuMTZWMzYuOTUxTDk0OS45NCAzOC4zNDJDOTUwLjEzIDQ0LjcwNCA5NTAuMTMgNTEuMjY1IDk1MC4xMyA1Ny42MjdWMTAyLjE2M0M5NTAuMTMgMTA4LjUyNSA5NDkuOTQgMTE0Ljg4NyA5NDkuOTQgMTIxLjI0OUw5MzcuMTYgMTIyLjY0MVYxMjkuNzk5SDk3OS4yOUM5ODcuNjcgMTI5Ljc5OSA5OTQuNjYgMTI5LjAwMyAxMDAwLjI1IDEyNy40MTNDMTAwNS44NSAxMjUuODIyIDEwMTAuNDQgMTIzLjYzNSAxMDEzLjYzIDEyMC44NTJDMTAxNy4wMyAxMTguMDY4IDEwMTkuNDIgMTE1LjA4NiAxMDIwLjgyIDExMS45MDVDMTAyMi40MiAxMDguNTI1IDEwMjMuMDIgMTA1LjM0NCAxMDIzLjAyIDEwMS45NjRDMTAyMy4wMiA5NS42MDIgMTAyMC42MiA5MC4yMzQgMTAxNi4wMyA4NS42NjFDMTAxMS40MyA4MS4wODggMTAwMy44NSA3OC4zMDUgOTkzLjI3IDc2LjkxM1pNOTY5LjcgNTYuNjMzQzk2OS45IDUwLjI3MSA5NjkuOSA0My45MDkgOTY5LjkgMzcuNTQ3SDk3Ny44OUM5ODQuNjggMzcuNTQ3IDk4OS44NyAzOC45MzggOTkzLjA3IDQxLjcyMkM5OTYuNDYgNDQuNTA2IDk5OC4yNiA0OC44OCA5OTguMjYgNTUuMDQzQzk5OC4yNiA2MS4yMDYgOTk2LjQ2IDY2LjE3NyA5OTIuODcgNjkuMzU4Qzk4OS4yNyA3Mi41MzkgOTgzLjQ4IDczLjkzMSA5NzUuNjkgNzMuOTMxSDk2OS41MUw5NjkuNyA1Ni42MzNaTTk3Ny4wOSAxMjEuODQ2SDk2OS45Qzk2OS43IDExNS40ODQgOTY5LjcgMTA5LjEyMSA5NjkuNyAxMDIuNTZWODEuNDg2SDk3Ni40OUM5ODUuNDggODEuNDg2IDk5Mi4wNyA4My4yNzUgOTk2LjI2IDg2LjY1NUMxMDAwLjQ1IDkwLjAzNSAxMDAyLjY1IDk1LjAwNSAxMDAyLjY1IDEwMS45NjRDMTAwMi42NSAxMTUuMDg2IDk5NC4yNiAxMjEuODQ2IDk3Ny4wOSAxMjEuODQ2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xNy4yNTkgMjEuNjI5QzIzLjI0OSAyMS42MjkgMjguMDQxIDE2Ljg1NyAyOC4wNDEgMTAuODkyNEMyOC4wNDEgNC45Mjc5IDIzLjI0OSAwLjE1NjE4OSAxNy4yNTkgMC4xNTYxODlDMTEuMjY4NyAwLjE1NjE4OSA2LjQ3NjU2IDQuOTI3OSA2LjQ3NjU2IDEwLjg5MjRDNi40NzY1NiAxNi44NTcgMTEuMjY4NyAyMS42MjkgMTcuMjU5IDIxLjYyOVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMjEuMDYzIDcwLjE1NUMzMC4yNDggNjcuOTY4IDM2LjAzOCA1OC44MjIgMzMuODQyIDQ5LjY3NkMzMS42NDYgNDAuNTMxIDIyLjQ2MSAzNC43NjUgMTMuMjc2IDM2Ljk1MkM0LjA5MDk3IDM5LjEzOSAtMS42OTk0MyA0OC4yODUgMC40OTY5NzIgNTcuNDNDMi42OTMyNyA2Ni43NzUgMTEuODc4MiA3Mi4zNDIgMjEuMDYzIDcwLjE1NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMjEuMDYzIDE1NS40NDhDMzAuMjQ4IDE1My4yNiAzNi4wMzggMTQ0LjExNSAzMy44NDIgMTM0Ljk2OUMzMS42NDYgMTI1LjgyNCAyMi40NjEgMTIwLjA1OCAxMy4yNzYgMTIyLjI0NUM0LjA5MDk3IDEyNC40MzIgLTEuNjk5NDMgMTMzLjU3OCAwLjQ5Njk3MiAxNDIuNzIzQzIuNjkzMjcgMTUxLjg2OSAxMS44NzgyIDE1Ny42MzUgMjEuMDYzIDE1NS40NDhaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTI3Ljg2OSA5Ni4xODVDMjcuODY5IDkwLjIyMSAyMy4wNzcgODUuNDQ5IDE3LjA4NyA4NS40NDlDMTEuMDk2OCA4NS40NDkgNi4zMDQ2OSA5MC4yMjEgNi4zMDQ2OSA5Ni4xODVDNi4zMDQ2OSAxMDIuMTUgMTEuMDk2OCAxMDYuOTIyIDE3LjA4NyAxMDYuOTIyQzIzLjA3NyAxMDYuOTIyIDI3Ljg2OSAxMDIuMTUgMjcuODY5IDk2LjE4NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNODIuOTc2OSA5NUM3My41OTE5IDk1IDY1LjgwNDkgMTAyLjU1NSA2NS44MDQ5IDExMi4wOThDNjUuODA0OSAxMjEuNDQzIDczLjM5MTkgMTI5LjE5NyA4Mi45NzY5IDEyOS4xOTdDOTIuMzYwOSAxMjkuMTk3IDEwMC4xNDggMTIxLjY0MSAxMDAuMTQ4IDExMi4wOThDOTkuOTQ3OSAxMDIuNTU1IDkyLjM2MDkgOTUgODIuOTc2OSA5NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNODIuOTc4MSAxNDMuOTAyQzc2Ljk4ODEgMTQzLjkwMiA3Mi4xOTUxIDE0OC42NzQgNzIuMTk1MSAxNTQuNjM5QzcyLjE5NTEgMTYwLjYwMyA3Ni45ODgxIDE2NS4zNzUgODIuOTc4MSAxNjUuMzc1Qzg4Ljk2ODEgMTY1LjM3NSA5My43NjAxIDE2MC42MDMgOTMuNzYwMSAxNTQuNjM5QzkzLjU2MDEgMTQ4LjY3NCA4OC43NjgxIDE0My45MDIgODIuOTc4MSAxNDMuOTAyWiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik04Mi45NzgxIDgwLjA4MkM4OC45NjgxIDgwLjA4MiA5My43NjAxIDc1LjMxIDkzLjc2MDEgNjkuMzQ1QzkzLjc2MDEgNjMuMzgxIDg4Ljk2ODEgNTguNjA5IDgyLjk3ODEgNTguNjA5Qzc2Ljk4ODEgNTguNjA5IDcyLjE5NTEgNjMuMzgxIDcyLjE5NTEgNjkuMzQ1QzcyLjE5NTEgNzUuMzEgNzYuOTg4MSA4MC4wODIgODIuOTc4MSA4MC4wODJaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTg0LjU2MDEgMzcuMzQ1QzkwLjM1MDEgMzYuMzUxIDk0LjM0MzEgMzAuOTgzIDkzLjM0NTEgMjUuMjE3QzkyLjM0NzEgMTkuNDUxIDg2Ljk1NjEgMTUuNDc1IDgxLjE2NTEgMTYuNDY5Qzc1LjM3NTEgMTcuNDYzIDcxLjM4MTEgMjIuODMxIDcyLjM4MDEgMjguNTk3QzczLjM3ODEgMzQuMzYzIDc4Ljc2OTEgMzguMTQgODQuNTYwMSAzNy4zNDVaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTE2MC42NDkgNjUuNTc5QzE2Ny4yMzggNTkuMDE4IDE2Ny4yMzggNDguMDgzIDE2MC42NDkgNDEuNTIyQzE1NC4wNiAzNC45NjEgMTQzLjA3OCAzNC45NjEgMTM2LjQ4OSA0MS41MjJDMTI5LjkgNDguMDgzIDEyOS45IDU5LjAxOCAxMzYuNDg5IDY1LjU3OUMxNDMuMDc4IDcyLjMzOSAxNTQuMDYgNzIuMzM5IDE2MC42NDkgNjUuNTc5WiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik0xNDguNjY1IDIxLjYyOUMxNTQuNjU1IDIxLjYyOSAxNTkuNDQ3IDE2Ljg1NyAxNTkuNDQ3IDEwLjg5MjRDMTU5LjQ0NyA0LjkyNzkgMTU0LjY1NSAwLjE1NjE4OSAxNDguNjY1IDAuMTU2MTg5QzE0Mi42NzUgMC4xNTYxODkgMTM3Ljg4MyA0LjkyNzkgMTM3Ljg4MyAxMC44OTI0QzEzNy44ODMgMTYuODU3IDE0Mi42NzUgMjEuNjI5IDE0OC42NjUgMjEuNjI5WiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik0xNDguNjY1IDg1LjY0OEMxNDIuNjc1IDg1LjY0OCAxMzcuODgzIDkwLjQyIDEzNy44ODMgOTYuMzg1QzEzNy44ODMgMTAyLjM0OSAxNDIuNjc1IDEwNy4xMjEgMTQ4LjY2NSAxMDcuMTIxQzE1NC42NTUgMTA3LjEyMSAxNTkuNDQ3IDEwMi4zNDkgMTU5LjQ0NyA5Ni4zODVDMTU5LjI0OCA5MC40MiAxNTQuNDU1IDg1LjY0OCAxNDguNjY1IDg1LjY0OFoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMTQ4LjY2NSAxMjguMjAzQzE0Mi42NzUgMTI4LjIwMyAxMzcuODgzIDEzMi45NzUgMTM3Ljg4MyAxMzguOTM5QzEzNy44ODMgMTQ0LjkwNCAxNDIuNjc1IDE0OS42NzUgMTQ4LjY2NSAxNDkuNjc1QzE1NC42NTUgMTQ5LjY3NSAxNTkuNDQ3IDE0NC45MDQgMTU5LjQ0NyAxMzguOTM5QzE1OS4yNDggMTMyLjk3NSAxNTQuNDU1IDEyOC4yMDMgMTQ4LjY2NSAxMjguMjAzWiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzdfMiI+PHJlY3Qgd2lkdGg9IjEzNjAiIGhlaWdodD0iMjY5IiBmaWxsPSJ3aGl0ZSI+PC9yZWN0PjwvY2xpcFBhdGg+PC9kZWZzPjwvc3ZnPg==" width="148" height="29" alt="Weights &amp; Biases by CoreWeave">
      <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" aria-hidden="true" focusable="false" viewBox="0 0 72 72" fill="none"><rect width="72" height="72" rx="36" fill="#EDE8FF" fill-opacity="0.12"></rect><path d="M36.1659 21.6895C41.0241 21.6897 45.0716 25.1548 45.9755 29.748C51.3234 29.0326 56.1659 33.1941 56.1659 38.6797C56.1659 43.6555 52.1318 47.6892 47.1561 47.6895H25.1757C20.1997 47.6894 16.1649 43.6556 16.1649 38.6797C16.1649 35.961 17.3551 33.5682 19.2059 31.9326C19.9773 32.4414 20.5763 33.0094 21.0643 33.6426C22.1003 34.987 22.7522 36.7636 23.3309 39.2793L23.3817 39.46C23.6686 40.3323 24.4749 40.7471 25.1639 40.7627C25.8996 40.7791 26.7901 40.3464 27.0614 39.3584L27.3231 38.4395C27.9393 36.3746 28.5952 34.8421 29.5155 33.6436C30.5327 32.3189 31.9633 31.2908 34.327 30.5029L34.4921 30.4395C35.2865 30.0954 35.6271 29.3281 35.6464 28.7061C35.6655 28.0853 35.3752 27.3045 34.6141 26.9082L34.4559 26.834C32.5926 26.0598 31.2457 25.0094 30.2059 23.6602C31.87 22.4223 33.9323 21.6895 36.1659 21.6895Z" fill="url(#cw-wb-inference-cloud)"></path><path d="M24.7928 38.9434C24.8886 39.3595 25.5021 39.3728 25.6151 38.9609C27.0322 33.7975 28.6807 30.8026 33.8524 29.0791C34.2316 28.9527 34.2489 28.3731 33.8798 28.2197C28.6774 26.0584 27.0289 21.9343 25.6075 16.4528C25.4999 16.0378 24.8913 16.0513 24.8004 16.4702C23.6132 21.9403 21.9564 26.0562 16.5205 28.2161C16.1441 28.3656 16.1611 28.9585 16.5469 29.0814C21.9515 30.8032 23.608 33.793 24.7928 38.9434Z" fill="url(#cw-wb-inference-sparkle)"></path><defs><linearGradient id="cw-wb-inference-cloud" x1="35.7572" y1="16.1487" x2="35.7572" y2="51.8348" gradientUnits="userSpaceOnUse"><stop offset="0.385417" stop-color="#FFCC33"></stop><stop offset="0.71875" stop-color="#FFAD33"></stop></linearGradient><linearGradient id="cw-wb-inference-sparkle" x1="35.7572" y1="16.1487" x2="35.7572" y2="51.8348" gradientUnits="userSpaceOnUse"><stop offset="0.385417" stop-color="#FFCC33"></stop><stop offset="0.71875" stop-color="#FFAD33"></stop></linearGradient></defs></svg>
      <span class="cw-wb-title">Inference</span>
      <span class="cw-wb-description">Explore hosted,<br>open-source LLMs</span>
      <span class="cw-wb-docs">Read docs <span aria-hidden="true">↗</span></span>
    </a>""")
    return (wandb_inference_card,)


@app.cell(hide_code=True)
def model_heading(wandb_inference_card):
    mo.hstack([
        mo.md("""
        ### Pick a model

        The effects are more pronounced in the small models, so let's stick with
        **Gemma 4 31B** model here. Here it runs through
        W&B Inference. The same selection is used everywhere downstream.
        Feel free to come back and try different models later.
        """),
        wandb_inference_card,
    ], align="start", widths=[0.72, 0.28], gap=1.5)
    return


@app.cell
def model_profiles():
    # Author-recommended starting points, checked 2026-09-09.
    # These are not a claim of optimal gridworld accuracy. Output budgets remain
    # separate demo controls; a token-limit finish is not proof of repetition.
    # W&B reasoning controls:
    # https://docs.wandb.ai/inference/response-settings/reasoning
    MODEL_CONFIGS = {
        "google/gemma-4-31B-it": {
            "sampling": {"temperature": 1.0, "top_p": 0.95},
            "extra_body": {"top_k": 64},
            "source": "https://huggingface.co/google/gemma-4-31B-it#best-practices",
            "note": "Google recommends this sampling in both modes; replaces the original demo's greedy off-mode.",
        },
        "deepseek-ai/DeepSeek-V4-Flash-0731": {
            "sampling": {"temperature": 1.0, "top_p": 1.0},
            "agent_sampling": {"top_p": 0.95},
            "source": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731#how-to-run-locally",
            "note": "DeepSeek recommends top_p=0.95 for agents and 1.0 otherwise.",
        },
        "deepseek-ai/DeepSeek-V4-Pro-0813": {
            "sampling": {"temperature": 1.0, "top_p": 1.0},
            "agent_sampling": {"top_p": 0.95},
            "source": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813",
            "note": "DeepSeek recommends top_p=0.95 for agents and 1.0 otherwise.",
        },
        "ibm-granite/granite-4.2-8b": {
            "sampling": {"temperature": 1.0, "top_p": 0.95},
            "source": "https://huggingface.co/ibm-granite/granite-4.2-8b#generation-parameters",
            "note": "IBM explicitly recommends these settings for chat, reasoning, and tools.",
        },
        "MiniMaxAI/MiniMax-M3": {
            "sampling": {"temperature": 1.0, "top_p": 0.95},
            "reasoning_flag": "thinking_mode",
            "reasoning_values": {True: "enabled", False: "disabled"},
            "source": "https://huggingface.co/MiniMaxAI/MiniMax-M3#inference-parameters",
            "template_source": "https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/chat_template.jinja",
            "note": "Use explicit template modes instead of the adaptive default; both modes checked on W&B.",
        },
        "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B": {
            "sampling": {"temperature": 1.0, "top_p": 0.95},
            "agent_template": {"force_nonempty_content": True},
            "source": "https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4#api-client",
            "note": "NVIDIA recommends the same sampling in both modes, plus force_nonempty_content for coding agents.",
        },
        "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B": {
            "sampling": {"temperature": 1.0, "top_p": 0.95},
            "agent_template": {"force_nonempty_content": True},
            "source": "https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16",
            "note": "NVIDIA recommends the same sampling in both modes; the tool template flag also covers SGLang serving.",
        },
        "Qwen/Qwen3.8-27B": {
            "sampling": {"temperature": 1.0, "top_p": 0.95, "presence_penalty": 0.0},
            "off_sampling": {"temperature": 0.7, "top_p": 0.8, "presence_penalty": 1.5},
            "extra_body": {"top_k": 20, "min_p": 0.0, "repetition_penalty": 1.0},
            "source": "https://huggingface.co/Qwen/Qwen3.8-27B#best-practices",
            "note": "Qwen specifies separate thinking and instruct profiles, including presence_penalty.",
        },
        "Qwen/Qwen3.6-35B-A3B": {
            "sampling": {"temperature": 1.0, "top_p": 0.95, "presence_penalty": 1.5},
            "off_sampling": {"temperature": 0.7, "top_p": 0.8, "presence_penalty": 1.5},
            "agent_on_sampling": {"temperature": 0.6, "presence_penalty": 0.0},
            "extra_body": {"top_k": 20, "min_p": 0.0, "repetition_penalty": 1.0},
            "source": "https://huggingface.co/Qwen/Qwen3.6-35B-A3B#best-practices",
            "note": "Use Qwen's general thinking profile for planning and precise-coding profile for the agent.",
        },
        "zai-org/GLM-5.2": {
            "sampling": {"temperature": 1.0, "top_p": 0.95},
            "agent_sampling": {"top_p": 1.0},
            "source": "https://huggingface.co/zai-org/GLM-5.2",
            "note": "Starting points from Z.ai's reasoning and SWE evaluations; no separate off-mode recommendation is published.",
        },
    }
    return (MODEL_CONFIGS,)


@app.cell(hide_code=True)
def model_catalog(API_KEY, ENTITY, MODEL_CONFIGS, PROJECT):
    mo.stop(not API_KEY, mo.md("_Connect to W&B above to load models._"))
    inference_client = openai.OpenAI(
        base_url="https://api.inference.wandb.ai/v1",
        api_key=API_KEY,
        project=f"{ENTITY}/{PROJECT}",
        timeout=90.0,
        max_retries=0,
    )
    # The configured profiles are also the single source for the selector.
    try:
        models_list = sorted({item.id for item in inference_client.models.list()} & set(MODEL_CONFIGS))
    except openai.OpenAIError as _error:
        mo.stop(True, mo.callout(
            mo.md("Could not load the W&B model catalog. Check your connection and rerun this cell.\n\n"
                  + str(_error).replace(API_KEY, "[redacted]")),
            kind="danger",
        ))
    mo.stop(not models_list, mo.md("_No shortlisted demo models are currently available._"))
    return inference_client, models_list


@app.cell(hide_code=True)
def model_controls(models_list):
    _preferred = "google/gemma-4-31B-it"
    model_selector = mo.ui.dropdown(
        options=models_list,
        value=_preferred if _preferred in models_list else models_list[0],
        label="Pick model",
        full_width=True,
    )
    model_selector
    return (model_selector,)


@app.cell(hide_code=True)
def planner_prompts(WORLD, gen_env):
    def build_world_prompt(env):
        lines = "\n".join(f"- {a['name']}: {a['doc']}" for a in env.actions_doc)
        base = env.to_prompt("structured")
        # The original notebook explicitly adds lava, omitted by to_prompt in 0.1.2.
        lava = sorted(env._puzzle.lava_set, key=lambda cell: (cell[1], cell[0]))
        if lava:
            base += "\nLava (walkable but instantly deadly; never step here): " + ", ".join(
                f"({x},{y})" for x, y in lava
            )
        return (
            "You are an agent in a 2D grid world. Plan a sequence of actions to "
            "collect every gem the world contains and finish on the goal tile, "
            "without ever stepping on lava. A solution counts ONLY when every gem "
            "has been collected AND you finish standing on the goal tile. Reaching "
            "the goal with gems still uncollected does NOT count. If there are no "
            "gems, you only need to reach the goal.\n\n"
            "Coordinates are (x, y), with x east and y south from the top-left. "
            "move_forward changes position by north=(x,y-1), east=(x+1,y), "
            "south=(x,y+1), west=(x-1,y). turn_right cycles north->east->south->west; "
            "turn_left cycles the reverse. Turning does not move you. "
            "Walls, water and blocking objects prevent movement. A blocked move "
            "leaves you in place. Lava is walkable but KILLS you; never step on it. "
            "A non-blocking gem is collected with collect_gem while standing on it, "
            "not automatically by walking onto it.\n\n"
            f"{base}\n\nAllowed actions:\n{lines}\n\n"
        )

    def build_planner_prompt(env):
        """The exact text the model sees: the structured world + its action space.
        ONE fixed, complete prompt for every world (lava + unambiguous action
        mechanics + non-presuppositional gems). Model-agnostic."""
        lines = "\n".join(f"- {a['name']}: {a['doc']}" for a in env.actions_doc)
        valid = ", ".join(a["name"] for a in env.actions_doc)
        base = env.to_prompt("structured")
        _lava = sorted(env._puzzle.lava_set, key=lambda cr: (cr[1], cr[0]))
        if _lava:
            base += (
                "\nLava (you CAN move onto these tiles, but stepping on lava "
                "KILLS you instantly -- never step here): "
                + ", ".join(f"({c},{r})" for c, r in _lava)
            )
        return (
            "You are an agent in a 2D grid world. Plan a sequence of actions to "
            "collect every gem the world contains and finish on the goal tile, "
            "without ever stepping on lava. A solution counts ONLY when every gem has been collected AND you finish standing on the goal tile -- reaching the goal tile with any gem still uncollected does NOT count (if the world has no gems, you only need to reach the goal). Coordinates are (x, y) with x going "
            "east and y going south from the top-left.\n\n"
            "How your actions work (the map's y points DOWN, so don't assume the "
            "usual math orientation): your facing is one of north/east/south/west. "
            "move_forward changes position by north=(x, y-1), east=(x+1, y), "
            "south=(x, y+1), west=(x-1, y). turn_right cycles your facing "
            "north->east->south->west->north; turn_left cycles the reverse "
            "(north->west->south->east->north).\n\n"
            f"{base}\n\n"
            f"Allowed actions:\n{lines}\n\n"
            "Output ONLY your final plan as a JSON array of action strings from: "
            f'{valid}\nExample: ["turn_right", "move_forward", "move_forward"]'
        )

    def parse_plan(text, valid):
        # Read a committed JSON list from the final answer, never from reasoning.
        for candidate in reversed(re.findall(r"\[[^\[\]]*\]", text, re.S)):
            try:
                plan = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if not isinstance(plan, list) or not all(isinstance(a, str) for a in plan):
                continue
            invalid = [a for a in plan if a not in valid]
            if invalid:
                raise ValueError(f"Unknown or disallowed actions: {invalid}")
            if len(plan) > 200:
                raise ValueError("The plan exceeds the 200-action limit.")
            return plan
        raise ValueError("The final answer did not contain a JSON list of action names.")

    PLANNER_PROMPT = build_planner_prompt(gen_env)
    GRIDWORLD_PROMPT = build_world_prompt(gen_env) + (
        """For this act, do not work the path out by hand. Write a Python function
    solve(world) that computes a plan using search or another algorithm.
    Return ONLY Python source, including any standard-library imports you need.
    Do not include markdown fences or an explanation.

    The caller invokes solve(world) in a Python 3.11 Sandbox and saves its returned
    list of action-name strings as JSON. Use at most 200 actions. Optimality is
    not required. Use only the standard library; Wanderland is not installed in
    the execution Sandbox. Do not use network access or external files.

    The dict below is the EXACT world argument your function receives:
    - cols and rows are dimensions; heading is a compass letter N/E/S/W.
    - start, goal, walls, gaps (water), lava and gems use [x,y] coordinate lists.
      Convert lists to tuples for set membership or tuple comparisons.
    - objects maps "x,y" strings to records with type, color, state and blocking.
    - pickup takes the object on the tile you FACE into your hand (capacity one).
    - toggle on a locked door you FACE unlocks it when you carry the matching-color
      key. You keep the key. An open door is passable.
    - collect_gem collects the non-blocking gem on the tile you STAND on.
    - The solution must collect EVERY gem AND finish on the goal without dying.

    """
        + json.dumps(WORLD, indent=2)
    )
    mo.accordion({"The direct-planning prompt": mo.md("~~~text\n" + PLANNER_PROMPT + "\n~~~")})
    return PLANNER_PROMPT, build_planner_prompt, parse_plan


@app.cell(hide_code=True)
def reasoning_capabilities(MODEL_CONFIGS):
    # All configured demo models support an explicit reasoning choice on W&B.
    THINKING_TOGGLE_MODELS = set(MODEL_CONFIGS)
    THINKING_ALWAYS_ON_MODELS = {
        "moonshotai/Kimi-K2.7-Code", "moonshotai/Kimi-K2.6",
        "openai/gpt-oss-120b", "openai/gpt-oss-20b", "zai-org/GLM-5.3-Flash",
    }

    def reasoning_options(model_name, thinking):
        """Translate the UI switch into the model's chat-template setting."""
        if thinking is None:
            return {}
        config = MODEL_CONFIGS[model_name]
        flag = config.get("reasoning_flag", "enable_thinking")
        value = config.get("reasoning_values", {True: True, False: False})[bool(thinking)]
        return {"chat_template_kwargs": {flag: value}}


    return THINKING_ALWAYS_ON_MODELS, THINKING_TOGGLE_MODELS, reasoning_options


@app.cell(hide_code=True)
def direct_controls(
    THINKING_ALWAYS_ON_MODELS,
    THINKING_TOGGLE_MODELS,
    model_selector,
):
    thinking_can_toggle = model_selector.value in THINKING_TOGGLE_MODELS
    thinking_always_on = model_selector.value in THINKING_ALWAYS_ON_MODELS
    reasoning_note = (
        "Run once with thinking off, then turn it on and compare." if thinking_can_toggle else
        "Reasoning stays on for this hosted model; an off mode isn't available." if thinking_always_on else
        "W&B does not document a reasoning toggle for this model; it uses the provider default."
    )
    reason_toggle = mo.ui.switch(value=thinking_always_on, label="🧠 thinking", disabled=not thinking_can_toggle)
    think_budget = mo.ui.slider(1024, 16384, value=8192, step=1024, label="output budget (tokens)")
    llm_seed = mo.ui.number(start=0, stop=99999, value=3407, label="🎲 LLM seed")
    ask_btn = mo.ui.run_button(label="Plan this world", kind="success")
    return (
        ask_btn,
        llm_seed,
        reason_toggle,
        reasoning_note,
        think_budget,
        thinking_always_on,
        thinking_can_toggle,
    )


@app.cell(hide_code=True)
def direct_controls_view(
    MODEL_CONFIGS,
    ask_btn,
    inference_options,
    llm_seed,
    model_selector,
    reason_toggle,
    reasoning_note,
    think_budget,
):
    mo.vstack([
        mo.hstack([ask_btn, reason_toggle, llm_seed], justify="start", gap=1.2),
        think_budget if reason_toggle.value else mo.md(""),
        mo.md(reasoning_note),
        mo.md("The seed fixes the requested sampling seed; the hosted service may still vary."),
        mo.md("[W&B reasoning controls](https://docs.wandb.ai/inference/response-settings/reasoning)"),
        mo.accordion({
        "Active model settings": mo.vstack([
            mo.md(MODEL_CONFIGS[model_selector.value]["note"]),
            mo.md("[Model author's guidance](" + MODEL_CONFIGS[model_selector.value]["source"] + ")"),
            mo.md("Settings are recommended starting points, not measured optima for this puzzle. Output budgets and seed are set separately."),
            mo.md("```json\n" + json.dumps({
                "direct": inference_options(model_selector.value, reason_toggle.value),
                "agent": inference_options(model_selector.value, reason_toggle.value, task="agent"),
            }, indent=2) + "\n```"),
        ])
    }),
    ])
    return


@app.cell
def inference_settings(MODEL_CONFIGS, reasoning_options):
    # Both inference paths resolve their settings here, including reasoning mode.
    def inference_options(model_name, thinking, *, task="direct"):
        """Build fresh W&B kwargs from the selected model, mode, and task."""
        if task not in {"direct", "agent"}:
            raise ValueError(f"Unknown inference task: {task}")
        if thinking is not True and thinking is not False:
            raise ValueError("Choose reasoning on or off for the configured demo models.")
        config = MODEL_CONFIGS[model_name]
        sampling = dict(config["sampling"])
        sampling.update(config.get("on_sampling" if thinking else "off_sampling", {}))
        extra = dict(config.get("extra_body", {}))
        extra.update(reasoning_options(model_name, thinking))
        if task == "agent":
            sampling.update(config.get("agent_sampling", {}))
            sampling.update(config.get("agent_on_sampling" if thinking else "agent_off_sampling", {}))
            extra["chat_template_kwargs"].update(config.get("agent_template", {}))
        return {**sampling, "extra_body": extra}


    return (inference_options,)


@app.cell(hide_code=True)
def direct_inference(inference_client, inference_options):
    def response_panel(reasoning, answer, busy=False):
        def text_box(text):
            return mo.Html(
                '<pre style="white-space:pre-wrap;overflow:auto;max-height:320px;'
                'padding:12px;border:1px solid #8884;border-radius:8px;font-size:0.8rem">'
                + html.escape(text) + "</pre>"
            )
        panels = []
        if reasoning:
            panels.extend([mo.md("**🧠 Reasoning**" + (" · streaming…" if busy else "")), text_box(reasoning)])
        panels.extend([
            mo.md("**Final answer**" + (" · waiting for the committed plan…" if busy and not answer else "")),
            text_box(answer) if answer else mo.md("_No final plan yet._"),
        ])
        return mo.vstack(panels)

    @weave.op(name="plan_world_direct", kind="llm")
    def plan_direct(model_name: str, prompt: str, thinking, max_tokens: int, seed: int) -> dict:
        started = time.monotonic()
        reasoning, answer = "", ""
        finish_reason, usage = None, None
        options = inference_options(model_name, thinking)
        with inference_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            seed=seed, max_tokens=max_tokens, **options,
            stream=True, stream_options={"include_usage": True},
        ) as stream:
            for index, chunk in enumerate(stream):
                if chunk.usage is not None:
                    usage = chunk.usage.model_dump()
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = choice.delta
                reasoning += getattr(delta, "reasoning", None) or getattr(delta, "reasoning_content", None) or ""
                answer += delta.content or ""
                finish_reason = choice.finish_reason or finish_reason
                if index % 16 == 0:
                    mo.output.replace(response_panel(reasoning, answer, busy=True))
        return {
            "model": model_name, "thinking": thinking, "reasoning": reasoning,
            "answer": answer, "finish_reason": finish_reason, "usage": usage,
            "request_options": options,
            "seconds": round(time.monotonic() - started, 2),
        }

    return plan_direct, response_panel


@app.cell(hide_code=True)
def direct_attempt(
    API_KEY,
    PLANNER_PROMPT,
    ask_btn,
    gen_env,
    gen_plan,
    gen_puzzle,
    llm_seed,
    model_selector,
    parse_plan,
    plan_direct,
    reason_toggle,
    response_panel,
    think_budget,
    thinking_can_toggle,
):
    mo.stop(not ask_btn.value, mo.md("_Press **Plan this world** to ask the model for actions directly._"))
    try:
        direct_response = plan_direct(
            model_selector.value, PLANNER_PROMPT,
            reason_toggle.value if thinking_can_toggle else None,
            int(think_budget.value) if reason_toggle.value else (
                1024 if model_selector.value == "google/gemma-4-31B-it" else 8192
            ),
            int(llm_seed.value),
        )
    except Exception as _error:
        mo.stop(True, mo.callout(
            mo.md("Inference failed: " + html.escape(str(_error).replace(API_KEY, "[redacted]"))),
            kind="danger",
        ))
    mo.stop(direct_response["finish_reason"] == "length", mo.vstack([
        response_panel(direct_response["reasoning"], direct_response["answer"]),
        mo.callout(mo.md(
            "The response hit the original 1,024-token non-thinking limit. Try another run or enable thinking."
            if model_selector.value == "google/gemma-4-31B-it" and not reason_toggle.value else
            "The response hit its token limit. Increase the budget and try again."
        ), kind="warn"),
    ]))
    try:
        direct_plan = parse_plan(direct_response["answer"], gen_env.action_space)
        direct_world = bp.World(gen_puzzle, speed=2.0)
        direct_verdict = direct_world.act(direct_plan)
    except Exception as _error:
        mo.stop(True, mo.vstack([
            response_panel(direct_response["reasoning"], direct_response["answer"]),
            mo.callout(mo.md(html.escape(str(_error))), kind="warn"),
        ]))
    direct_scene = mo.ui.anywidget(direct_world)
    _mode = (
        "with reasoning" if direct_response["thinking"] is True else
        "no reasoning" if direct_response["thinking"] is False else "provider default"
    )
    _status = "🎉 solved it!" if direct_verdict["success"] else (
        "💀 walked into lava" if direct_verdict["died"] else "didn't solve it"
    )
    mo.vstack([
        response_panel(direct_response["reasoning"], direct_response["answer"]),
        direct_scene,
        mo.callout(mo.md(
            f"The model's attempt: **{_status}** · {_mode}\n\n"
            f"- Plan: **{len(direct_plan)} actions** (oracle: {len(gen_plan)})\n"
            f"- Gems: **{direct_verdict['gems_collected']}/{direct_verdict['total_gems']}** · "
            f"Goal reached: **{direct_verdict['reached_goal']}**\n"
            f"- Inference: **{direct_response['seconds']:.1f}s**\n\n"
            "Press **Run My Code** in the scene to watch it play out."
        ), kind="success" if direct_verdict["success"] else "warn"),
    ])
    return


@app.cell(hide_code=True)
def act3_intro():
    mo.md("""
    ## Act 3 · When planning doesn't scale, write a planner

    We have tried planning the world in our heads and asked a language model to
    do the same. As the map grows, there are more tiles, turns and objects to keep
    track of. Our BFS oracle treats that as a search problem.

    So here's a different idea. What if the model doesn't plan the world at all,
    but instead **writes a program that does**? Give it a Sandbox, let it write
    its own little oracle, run that code, and read back the plan.

    Its job changes from “trace every step perfectly in my head” to “write a
    search, once.” This is the code-writing agent: the model proposes a program,
    the Sandbox executes it, and Wanderland checks the returned actions.

    Use the same model and generated world from Act 2. One click writes the code,
    runs it in a Sandbox, and checks the returned plan in Wanderland.

    Turn on **Close the loop** to send Python errors and failed-plan feedback back
    to the model. It can fix its program and try again, for up to six turns. A
    verified solution ends the loop immediately; then watch Mo play the result.
    """)
    return


@app.cell(hide_code=True)
def wandb_sandboxes_feature():
    # Official logo: https://site.wandb.ai/wp-content/uploads/2023/05/wb-cw.svg
    # Card styling matches the Inference card; cube illustration uses the same palette.
    # Documentation: https://docs.wandb.ai/sandboxes
    wandb_sandboxes_card = mo.Html(r"""<style>
    .cw-wb-sandboxes-card {
      box-sizing: border-box; display: flex; flex-direction: column; align-items: center;
      gap: 10px; width: 180px; max-width: 100%; padding: 16px; margin-left: auto;
      background: #20242b; border: 1px solid #4b535c; border-radius: 8px;
      color: #fff !important; text-align: center; text-decoration: none !important;
      font-family: "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
      transition: transform .2s, border-color .2s;
    }
    .cw-wb-sandboxes-card:hover {transform: translateY(-4px); border-color: #ffcc33;}
    .cw-wb-sandboxes-card:focus-visible {outline: 3px solid #ffcc33; outline-offset: 4px;}
    .cw-wb-sandboxes-card svg {display: block; flex-shrink: 0;}
    .cw-wb-sandboxes-card .cw-wb-brand {display:block; width:148px; max-width:100%; height:auto; margin:0 0 4px;}
    .cw-wb-sandboxes-card .cw-wb-title {font-size: 20px; line-height: 26px; font-weight: 400;}
    .cw-wb-sandboxes-card .cw-wb-description {font-size: 13px; line-height: 17px; color: #aeb3bd;}
    .cw-wb-sandboxes-card .cw-wb-docs {font-size: 12px; line-height: 18px; color: #ffcc33; font-weight: 600;}
    @media (prefers-reduced-motion: reduce) {
      .cw-wb-sandboxes-card {transition: none;}
    }
    </style>
    <a class="cw-wb-sandboxes-card" href="https://docs.wandb.ai/sandboxes"
       target="_blank" rel="noopener noreferrer" aria-label="W&B Serverless Sandboxes documentation">
      <img class="cw-wb-brand" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMzYwIiBoZWlnaHQ9IjI2OSIgdmlld0JveD0iMCAwIDEzNjAgMjY5IiBmaWxsPSJub25lIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfN18yKSI+PHBhdGggZD0iTTgzMC4wNDUgMjUyLjI4M0M4MjYuNzUyIDI1Mi4yODMgODIzLjczNyAyNTEuNTQ4IDgyMS4wMDEgMjUwLjA3OUM4MTguMzE2IDI0OC42MSA4MTYuMjM5IDI0Ni41MzIgODE0Ljc2OSAyNDMuODQ3TDgxNS43NTcgMjQyLjYzMVYyNTEuMzcxSDgwOC44NDFWMTkzLjgzOUg4MTUuOTA5VjIxOS4yMjNMODE0Ljg0NSAyMTcuNDc1QzgxNi4zNjUgMjE1LjA0MyA4MTguNDQzIDIxMy4xMTggODIxLjA3NyAyMTEuNjk5QzgyMy43MTIgMjEwLjIzIDgyNi43MjcgMjA5LjQ5NSA4MzAuMTIxIDIwOS40OTVDODMzLjk3MiAyMDkuNDk1IDgzNy40MTcgMjEwLjQzMiA4NDAuNDU3IDIxMi4zMDdDODQzLjU0OCAyMTQuMTgyIDg0NS45OCAyMTYuNzQgODQ3Ljc1MyAyMTkuOTgzQzg0OS41MjcgMjIzLjE3NSA4NTAuNDEzIDIyNi44MjMgODUwLjQxMyAyMzAuOTI3Qzg1MC40MTMgMjM0LjkzIDg0OS41MjcgMjM4LjU1MiA4NDcuNzUzIDI0MS43OTVDODQ1Ljk4IDI0NS4wMzggODQzLjU0OCAyNDcuNTk2IDg0MC40NTcgMjQ5LjQ3MUM4MzcuNDE3IDI1MS4zNDYgODMzLjk0NyAyNTIuMjgzIDgzMC4wNDUgMjUyLjI4M1pNODI5LjUxMyAyNDUuNDQzQzgzMi4wOTcgMjQ1LjQ0MyA4MzQuNDAzIDI0NC44MSA4MzYuNDI5IDI0My41NDNDODM4LjQ1NiAyNDIuMjc2IDg0MC4wMjcgMjQwLjU1NCA4NDEuMTQxIDIzOC4zNzVDODQyLjMwNyAyMzYuMTQ2IDg0Mi44ODkgMjMzLjY2MyA4NDIuODg5IDIzMC45MjdDODQyLjg4OSAyMjguMDkgODQyLjMwNyAyMjUuNjA3IDg0MS4xNDEgMjIzLjQ3OUM4NDAuMDI3IDIyMS4zIDgzOC40NTYgMjE5LjU3OCA4MzYuNDI5IDIxOC4zMTFDODM0LjQwMyAyMTYuOTk0IDgzMi4wOTcgMjE2LjMzNSA4MjkuNTEzIDIxNi4zMzVDODI2LjkyOSAyMTYuMzM1IDgyNC41OTkgMjE2Ljk2OCA4MjIuNTIxIDIxOC4yMzVDODIwLjQ5NSAyMTkuNTAyIDgxOC44NzMgMjIxLjI1IDgxNy42NTcgMjIzLjQ3OUM4MTYuNDkyIDIyNS42NTggODE1LjkwOSAyMjguMTQgODE1LjkwOSAyMzAuOTI3QzgxNS45MDkgMjMzLjY2MyA4MTYuNDkyIDIzNi4xNDYgODE3LjY1NyAyMzguMzc1QzgxOC44NzMgMjQwLjU1NCA4MjAuNDk1IDI0Mi4yNzYgODIyLjUyMSAyNDMuNTQzQzgyNC41OTkgMjQ0LjgxIDgyNi45MjkgMjQ1LjQ0MyA4MjkuNTEzIDI0NS40NDNaTTg2My40MjMgMjY4LjA5MUM4NjIuNTExIDI2OC4wOTEgODYxLjU5OSAyNjguMDE1IDg2MC42ODcgMjY3Ljg2M0M4NTkuNzc1IDI2Ny43MTEgODU4LjkxNCAyNjcuNDU4IDg1OC4xMDMgMjY3LjEwM1YyNjAuNzk1Qzg1OC42NiAyNjAuODk2IDg1OS4zNDQgMjYwLjk5OCA4NjAuMTU1IDI2MS4wOTlDODYxLjAxNiAyNjEuMjUxIDg2MS44NTIgMjYxLjMyNyA4NjIuNjYzIDI2MS4zMjdDODY1LjA0NCAyNjEuMzI3IDg2Ni44NDMgMjYwLjc5NSA4NjguMDU5IDI1OS43MzFDODY5LjMyNiAyNTguNzE4IDg3MC41MTYgMjU2Ljk0NCA4NzEuNjMxIDI1NC40MTFMODc0LjIxNSAyNDguMjU1TDg3NC4wNjMgMjU0LjQxMUw4NTYuNTgzIDIxMC40MDdIODY0LjI1OUw4NzcuODYzIDI0NS4zNjdIODc1LjU4M0w4ODkuMTExIDIxMC40MDdIODk2LjkzOUw4NzguNDcxIDI1Ni4yMzVDODc3LjYxIDI1OC40MTQgODc2LjQ5NSAyNjAuMzkgODc1LjEyNyAyNjIuMTYzQzg3My44MSAyNjMuOTg3IDg3Mi4xODggMjY1LjQzMSA4NzAuMjYzIDI2Ni40OTVDODY4LjMzOCAyNjcuNTU5IDg2Ni4wNTggMjY4LjA5MSA4NjMuNDIzIDI2OC4wOTFaTTk0Ny44MyAyNTIuMjgzQzk0My44MiAyNTIuMjgzIDk0MC4xMyAyNTEuNTc0IDkzNi43MyAyNTAuMTU1QzkzMy4zOSAyNDguNjg2IDkzMC40NSAyNDYuNjM0IDkyNy45MiAyNDMuOTk5QzkyNS40MyAyNDEuMzY0IDkyMy41MSAyMzguMjc0IDkyMi4xNCAyMzQuNzI3QzkyMC43NyAyMzEuMTggOTIwLjA5IDIyNy4zMDQgOTIwLjA5IDIyMy4wOTlDOTIwLjA5IDIxOC44NDMgOTIwLjc3IDIxNC45NDIgOTIyLjE0IDIxMS4zOTVDOTIzLjUxIDIwNy44NDggOTI1LjQzIDIwNC43NTggOTI3LjkyIDIwMi4xMjNDOTMwLjQgMTk5LjQ4OCA5MzMuMzQgMTk3LjQ2MiA5MzYuNzMgMTk2LjA0M0M5NDAuMTMgMTk0LjU3NCA5NDMuODIgMTkzLjgzOSA5NDcuODMgMTkzLjgzOUM5NTEuNzMgMTkzLjgzOSA5NTUuMjIgMTk0LjUyMyA5NTguMzIgMTk1Ljg5MUM5NjEuNDYgMTk3LjI1OSA5NjQuMDkgMTk5LjAzMiA5NjYuMjIgMjAxLjIxMUM5NjguNCAyMDMuMzkgOTY5Ljk0IDIwNS43MiA5NzAuODYgMjA4LjIwM0w5NjQuMDIgMjExLjMxOUM5NjIuNyAyMDguMTc4IDk2MC42NSAyMDUuNjQ0IDk1Ny44NiAyMDMuNzE5Qzk1NS4wNyAyMDEuNzQzIDk1MS43MyAyMDAuNzU1IDk0Ny44MyAyMDAuNzU1Qzk0My44OCAyMDAuNzU1IDk0MC4zNSAyMDEuNjkyIDkzNy4yNiAyMDMuNTY3QzkzNC4yMiAyMDUuNDQyIDkzMS44NCAyMDguMDUxIDkzMC4xMiAyMTEuMzk1QzkyOC40IDIxNC43MzkgOTI3LjU0IDIxOC42NCA5MjcuNTQgMjIzLjA5OUM5MjcuNTQgMjI3LjUwNyA5MjguNCAyMzEuMzgzIDkzMC4xMiAyMzQuNzI3QzkzMS44NCAyMzguMDcxIDkzNC4yMiAyNDAuNjggOTM3LjI2IDI0Mi41NTVDOTQwLjM1IDI0NC40MyA5NDMuODggMjQ1LjM2NyA5NDcuODMgMjQ1LjM2N0M5NTEuNzMgMjQ1LjM2NyA5NTUuMDcgMjQ0LjQwNCA5NTcuODYgMjQyLjQ3OUM5NjAuNjUgMjQwLjUwMyA5NjIuNyAyMzcuOTQ0IDk2NC4wMiAyMzQuODAzTDk3MC44NiAyMzcuOTE5Qzk2OS45NCAyNDAuNDAyIDk2OC40IDI0Mi43MzIgOTY2LjIyIDI0NC45MTFDOTY0LjA5IDI0Ny4wOSA5NjEuNDYgMjQ4Ljg2MyA5NTguMzIgMjUwLjIzMUM5NTUuMjIgMjUxLjU5OSA5NTEuNzMgMjUyLjI4MyA5NDcuODMgMjUyLjI4M1pNMTAwMS4xNCAyNTIuMjgzQzk5Ny4xOSAyNTIuMjgzIDk5My42MiAyNTEuMzcxIDk5MC40MyAyNDkuNTQ3Qzk4Ny4yNCAyNDcuNjcyIDk4NC43IDI0NS4xMTQgOTgyLjgzIDI0MS44NzFDOTgwLjk1IDIzOC42MjggOTgwLjAyIDIzNC45NTUgOTgwLjAyIDIzMC44NTFDOTgwLjAyIDIyNi43NDcgOTgwLjkzIDIyMy4wOTkgOTgyLjc1IDIxOS45MDdDOTg0LjYzIDIxNi43MTUgOTg3LjE2IDIxNC4xODIgOTkwLjM1IDIxMi4zMDdDOTkzLjU0IDIxMC40MzIgOTk3LjE0IDIwOS40OTUgMTAwMS4xNCAyMDkuNDk1QzEwMDUuMSAyMDkuNDk1IDEwMDguNjcgMjEwLjQzMiAxMDExLjg2IDIxMi4zMDdDMTAxNS4wNSAyMTQuMTMxIDEwMTcuNTYgMjE2LjYzOSAxMDE5LjM4IDIxOS44MzFDMTAyMS4yNiAyMjMuMDIzIDEwMjIuMiAyMjYuNjk2IDEwMjIuMiAyMzAuODUxQzEwMjIuMiAyMzUuMDA2IDEwMjEuMjMgMjM4LjcwNCAxMDE5LjMxIDI0MS45NDdDMTAxNy4zOCAyNDUuMTM5IDEwMTQuODIgMjQ3LjY3MiAxMDExLjYzIDI0OS41NDdDMTAwOC40OSAyNTEuMzcxIDEwMDQuOTkgMjUyLjI4MyAxMDAxLjE0IDI1Mi4yODNaTTEwMDEuMTQgMjQ1LjQ0M0MxMDAzLjY4IDI0NS40NDMgMTAwNS45NiAyNDQuODEgMTAwNy45OCAyNDMuNTQzQzEwMTAuMDYgMjQyLjI3NiAxMDExLjY4IDI0MC41MjggMTAxMi44NSAyMzguMjk5QzEwMTQuMDYgMjM2LjA3IDEwMTQuNjcgMjMzLjU4NyAxMDE0LjY3IDIzMC44NTFDMTAxNC42NyAyMjguMDY0IDEwMTQuMDYgMjI1LjYwNyAxMDEyLjg1IDIyMy40NzlDMTAxMS42OCAyMjEuMyAxMDEwLjA2IDIxOS41NzggMTAwNy45OCAyMTguMzExQzEwMDUuOTYgMjE2Ljk5NCAxMDAzLjY4IDIxNi4zMzUgMTAwMS4xNCAyMTYuMzM1Qzk5OC41NiAyMTYuMzM1IDk5Ni4yMyAyMTYuOTk0IDk5NC4xNSAyMTguMzExQzk5Mi4xMyAyMTkuNTc4IDk5MC41IDIyMS4zIDk4OS4yOSAyMjMuNDc5Qzk4OC4wNyAyMjUuNjA3IDk4Ny40NiAyMjguMDY0IDk4Ny40NiAyMzAuODUxQzk4Ny40NiAyMzMuNTg3IDk4OC4wNyAyMzYuMDcgOTg5LjI5IDIzOC4yOTlDOTkwLjUgMjQwLjUyOCA5OTIuMTMgMjQyLjI3NiA5OTQuMTUgMjQzLjU0M0M5OTYuMjMgMjQ0LjgxIDk5OC41NiAyNDUuNDQzIDEwMDEuMTQgMjQ1LjQ0M1pNMTAzMy42OSAyNTEuMzcxVjIxMC40MDdIMTA0MC42MVYyMTcuOTMxTDEwMzkuODUgMjE2Ljg2N0MxMDQwLjgxIDIxNC41MzYgMTA0Mi4yOCAyMTIuODE0IDEwNDQuMjYgMjExLjY5OUMxMDQ2LjIzIDIxMC41MzQgMTA0OC42NCAyMDkuOTUxIDEwNTEuNDggMjA5Ljk1MUgxMDUzLjk5VjIxNi42MzlIMTA1MC40MUMxMDQ3LjUzIDIxNi42MzkgMTA0NS4yIDIxNy41NTEgMTA0My40MiAyMTkuMzc1QzEwNDEuNjUgMjIxLjE0OCAxMDQwLjc2IDIyMy42ODIgMTA0MC43NiAyMjYuOTc1VjI1MS4zNzFIMTAzMy42OVpNMTA4MS4zOSAyNTIuMjgzQzEwNzcuNDQgMjUyLjI4MyAxMDczLjkyIDI1MS4zNDYgMTA3MC44MyAyNDkuNDcxQzEwNjcuNzQgMjQ3LjU5NiAxMDY1LjMxIDI0NS4wMzggMTA2My41MyAyNDEuNzk1QzEwNjEuNzYgMjM4LjUwMiAxMDYwLjg3IDIzNC44MjggMTA2MC44NyAyMzAuNzc1QzEwNjAuODcgMjI2LjY3MSAxMDYxLjczIDIyMy4wMjMgMTA2My40NiAyMTkuODMxQzEwNjUuMjMgMjE2LjYzOSAxMDY3LjYxIDIxNC4xMzEgMTA3MC42IDIxMi4zMDdDMTA3My42NCAyMTAuNDMyIDEwNzcuMDQgMjA5LjQ5NSAxMDgwLjc4IDIwOS40OTVDMTA4My44MiAyMDkuNDk1IDEwODYuNTEgMjEwLjA1MiAxMDg4Ljg0IDIxMS4xNjdDMTA5MS4yMiAyMTIuMjMxIDEwOTMuMjIgMjEzLjcgMTA5NC44NCAyMTUuNTc1QzEwOTYuNTIgMjE3LjM5OSAxMDk3Ljc4IDIxOS41MDIgMTA5OC42NCAyMjEuODgzQzEwOTkuNTYgMjI0LjIxNCAxMTAwLjAxIDIyNi42NDYgMTEwMC4wMSAyMjkuMTc5QzExMDAuMDEgMjI5LjczNiAxMDk5Ljk2IDIzMC4zNyAxMDk5Ljg2IDIzMS4wNzlDMTA5OS44MSAyMzEuNzM4IDEwOTkuNzMgMjMyLjM3MSAxMDk5LjYzIDIzMi45NzlIMTA2Ni4wNFYyMjYuODk5SDEwOTUuNTNMMTA5Mi4xOCAyMjkuNjM1QzEwOTIuNjQgMjI3IDEwOTIuMzkgMjI0LjY0NCAxMDkxLjQyIDIyMi41NjdDMTA5MC40NiAyMjAuNDkgMTA4OS4wNCAyMTguODQzIDEwODcuMTcgMjE3LjYyN0MxMDg1LjI5IDIxNi40MTEgMTA4My4xNyAyMTUuODAzIDEwODAuNzggMjE1LjgwM0MxMDc4LjQgMjE1LjgwMyAxMDc2LjIyIDIxNi40MTEgMTA3NC4yNSAyMTcuNjI3QzEwNzIuMjcgMjE4Ljg0MyAxMDcwLjczIDIyMC41OTEgMTA2OS42MSAyMjIuODcxQzEwNjguNTUgMjI1LjEgMTA2OC4xMiAyMjcuNzYgMTA2OC4zMiAyMzAuODUxQzEwNjguMTIgMjMzLjg0IDEwNjguNTcgMjM2LjQ3NSAxMDY5LjY5IDIzOC43NTVDMTA3MC44NSAyNDAuOTg0IDEwNzIuNDggMjQyLjczMiAxMDc0LjU1IDI0My45OTlDMTA3Ni42OCAyNDUuMjE1IDEwNzguOTkgMjQ1LjgyMyAxMDgxLjQ3IDI0NS44MjNDMTA4NC4yIDI0NS44MjMgMTA4Ni41MSAyNDUuMTkgMTA4OC4zOCAyNDMuOTIzQzEwOTAuMjYgMjQyLjY1NiAxMDkxLjc4IDI0MS4wMzUgMTA5Mi45NCAyMzkuMDU5TDEwOTguODcgMjQyLjA5OUMxMDk4LjA2IDI0My45NzQgMTA5Ni44IDI0NS42OTYgMTA5NS4wNyAyNDcuMjY3QzEwOTMuNCAyNDguNzg3IDEwOTEuNCAyNTAuMDAzIDEwODkuMDcgMjUwLjkxNUMxMDg2Ljc5IDI1MS44MjcgMTA4NC4yMyAyNTIuMjgzIDEwODEuMzkgMjUyLjI4M1pNMTEyMi43NiAyNTEuMzcxTDExMDYuODcgMTk0Ljc1MUgxMTE0LjdMMTEyOCAyNDQuNjA3SDExMjYuMThMMTE0MC4wMSAxOTQuNzUxSDExNDcuODRMMTE2MS41OSAyNDQuNjA3SDExNTkuNjlMMTE3My4wNyAxOTQuNzUxSDExODAuOUwxMTY1LjAxIDI1MS4zNzFIMTE1Ni43M0wxMTQyLjkgMjAxLjc0M0gxMTQ0Ljg3TDExMzEuMDQgMjUxLjM3MUgxMTIyLjc2Wk0xMjA1LjUyIDI1Mi4yODNDMTIwMS41NyAyNTIuMjgzIDExOTguMDUgMjUxLjM0NiAxMTk0Ljk2IDI0OS40NzFDMTE5MS44NiAyNDcuNTk2IDExODkuNDMgMjQ1LjAzOCAxMTg3LjY2IDI0MS43OTVDMTE4NS44OSAyMzguNTAyIDExODUgMjM0LjgyOCAxMTg1IDIzMC43NzVDMTE4NSAyMjYuNjcxIDExODUuODYgMjIzLjAyMyAxMTg3LjU4IDIxOS44MzFDMTE4OS4zNiAyMTYuNjM5IDExOTEuNzQgMjE0LjEzMSAxMTk0LjczIDIxMi4zMDdDMTE5Ny43NyAyMTAuNDMyIDEyMDEuMTYgMjA5LjQ5NSAxMjA0LjkxIDIwOS40OTVDMTIwNy45NSAyMDkuNDk1IDEyMTAuNjQgMjEwLjA1MiAxMjEyLjk3IDIxMS4xNjdDMTIxNS4zNSAyMTIuMjMxIDEyMTcuMzUgMjEzLjcgMTIxOC45NyAyMTUuNTc1QzEyMjAuNjQgMjE3LjM5OSAxMjIxLjkxIDIxOS41MDIgMTIyMi43NyAyMjEuODgzQzEyMjMuNjggMjI0LjIxNCAxMjI0LjE0IDIyNi42NDYgMTIyNC4xNCAyMjkuMTc5QzEyMjQuMTQgMjI5LjczNiAxMjI0LjA5IDIzMC4zNyAxMjIzLjk5IDIzMS4wNzlDMTIyMy45NCAyMzEuNzM4IDEyMjMuODYgMjMyLjM3MSAxMjIzLjc2IDIzMi45NzlIMTE5MC4xN1YyMjYuODk5SDEyMTkuNjZMMTIxNi4zMSAyMjkuNjM1QzEyMTYuNzcgMjI3IDEyMTYuNTEgMjI0LjY0NCAxMjE1LjU1IDIyMi41NjdDMTIxNC41OSAyMjAuNDkgMTIxMy4xNyAyMTguODQzIDEyMTEuMyAyMTcuNjI3QzEyMDkuNDIgMjE2LjQxMSAxMjA3LjI5IDIxNS44MDMgMTIwNC45MSAyMTUuODAzQzEyMDIuNTMgMjE1LjgwMyAxMjAwLjM1IDIxNi40MTEgMTE5OC4zOCAyMTcuNjI3QzExOTYuNCAyMTguODQzIDExOTQuODUgMjIwLjU5MSAxMTkzLjc0IDIyMi44NzFDMTE5Mi42OCAyMjUuMSAxMTkyLjI0IDIyNy43NiAxMTkyLjQ1IDIzMC44NTFDMTE5Mi4yNCAyMzMuODQgMTE5Mi43IDIzNi40NzUgMTE5My44MiAyMzguNzU1QzExOTQuOTggMjQwLjk4NCAxMTk2LjYgMjQyLjczMiAxMTk4LjY4IDI0My45OTlDMTIwMC44MSAyNDUuMjE1IDEyMDMuMTEgMjQ1LjgyMyAxMjA1LjYgMjQ1LjgyM0MxMjA4LjMzIDI0NS44MjMgMTIxMC42NCAyNDUuMTkgMTIxMi41MSAyNDMuOTIzQzEyMTQuMzkgMjQyLjY1NiAxMjE1LjkxIDI0MS4wMzUgMTIxNy4wNyAyMzkuMDU5TDEyMjMgMjQyLjA5OUMxMjIyLjE5IDI0My45NzQgMTIyMC45MiAyNDUuNjk2IDEyMTkuMiAyNDcuMjY3QzEyMTcuNTMgMjQ4Ljc4NyAxMjE1LjUzIDI1MC4wMDMgMTIxMy4yIDI1MC45MTVDMTIxMC45MiAyNTEuODI3IDEyMDguMzYgMjUyLjI4MyAxMjA1LjUyIDI1Mi4yODNaTTEyNDcuMTIgMjUyLjI4M0MxMjQ0LjQ0IDI1Mi4yODMgMTI0Mi4wNiAyNTEuODAyIDEyMzkuOTggMjUwLjgzOUMxMjM3Ljk1IDI0OS44MjYgMTIzNi4zNiAyNDguNDU4IDEyMzUuMTkgMjQ2LjczNUMxMjM0LjAzIDI0NC45NjIgMTIzMy40NCAyNDIuOTM1IDEyMzMuNDQgMjQwLjY1NUMxMjMzLjQ0IDIzOC40NzYgMTIzMy45IDIzNi41MjYgMTIzNC44MSAyMzQuODAzQzEyMzUuNzcgMjMzLjAzIDEyMzcuMjQgMjMxLjUzNSAxMjM5LjIyIDIzMC4zMTlDMTI0MS4yNSAyMjkuMTAzIDEyNDMuNzggMjI4LjI0MiAxMjQ2LjgyIDIyNy43MzVMMTI2Mi4wMiAyMjUuMjI3VjIzMS4xNTVMMTI0OC40MiAyMzMuNDM1QzEyNDUuNzggMjMzLjg5MSAxMjQzLjg2IDIzNC43MjcgMTI0Mi42NCAyMzUuOTQzQzEyNDEuNDcgMjM3LjE1OSAxMjQwLjg5IDIzOC42NTQgMTI0MC44OSAyNDAuNDI3QzEyNDAuODkgMjQyLjA5OSAxMjQxLjU1IDI0My40OTIgMTI0Mi44NyAyNDQuNjA3QzEyNDQuMjQgMjQ1LjcyMiAxMjQ1LjkzIDI0Ni4yNzkgMTI0Ny45NiAyNDYuMjc5QzEyNTAuNTQgMjQ2LjI3OSAxMjUyLjc3IDI0NS43NDcgMTI1NC42NSAyNDQuNjgzQzEyNTYuNTcgMjQzLjU2OCAxMjU4LjA3IDI0Mi4wNzQgMTI1OS4xMyAyNDAuMTk5QzEyNjAuMjUgMjM4LjMyNCAxMjYwLjggMjM2LjI0NyAxMjYwLjggMjMzLjk2N1YyMjMuNTU1QzEyNjAuOCAyMjEuMzI2IDEyNTkuOTcgMjE5LjUyNyAxMjU4LjMgMjE4LjE1OUMxMjU2LjY3IDIxNi43NCAxMjU0LjUyIDIxNi4wMzEgMTI1MS44NCAyMTYuMDMxQzEyNDkuNSAyMTYuMDMxIDEyNDcuNDMgMjE2LjYzOSAxMjQ1LjYgMjE3Ljg1NUMxMjQzLjgzIDIxOS4wMiAxMjQyLjUxIDIyMC41OTEgMTI0MS42NSAyMjIuNTY3TDEyMzUuNSAyMTkuMzc1QzEyMzYuMjYgMjE3LjUgMTIzNy40NyAyMTUuODI4IDEyMzkuMTQgMjE0LjM1OUMxMjQwLjgyIDIxMi44MzkgMTI0Mi43NyAyMTEuNjQ4IDEyNDUgMjEwLjc4N0MxMjQ3LjIyIDIwOS45MjYgMTI0OS41NiAyMDkuNDk1IDEyNTEuOTkgMjA5LjQ5NUMxMjU1LjEzIDIwOS40OTUgMTI1Ny44OSAyMTAuMTAzIDEyNjAuMjcgMjExLjMxOUMxMjYyLjY1IDIxMi40ODQgMTI2NC41IDIxNC4xMzEgMTI2NS44MiAyMTYuMjU5QzEyNjcuMTkgMjE4LjMzNiAxMjY3Ljg3IDIyMC43NjggMTI2Ny44NyAyMjMuNTU1VjI1MS4zNzFIMTI2MC45NlYyNDMuNjE5TDEyNjIuMjUgMjQ0LjA3NUMxMjYxLjM5IDI0NS42OTYgMTI2MC4yMiAyNDcuMTE1IDEyNTguNzUgMjQ4LjMzMUMxMjU3LjI4IDI0OS41NDcgMTI1NS41NiAyNTAuNTEgMTI1My41OCAyNTEuMjE5QzEyNTEuNjEgMjUxLjkyOCAxMjQ5LjQ1IDI1Mi4yODMgMTI0Ny4xMiAyNTIuMjgzWk0xMjkxLjc3IDI1MS4zNzFMMTI3NS43MyAyMTAuNDA3SDEyODMuNjRMMTI5Ni40OCAyNDUuMDYzSDEyOTMuNzRMMTMwNi42NiAyMTAuNDA3SDEzMTQuNTdMMTI5OC40NiAyNTEuMzcxSDEyOTEuNzdaTTEzNDEuMjggMjUyLjI4M0MxMzM3LjMzIDI1Mi4yODMgMTMzMy44IDI1MS4zNDYgMTMzMC43MSAyNDkuNDcxQzEzMjcuNjIgMjQ3LjU5NiAxMzI1LjE5IDI0NS4wMzggMTMyMy40MiAyNDEuNzk1QzEzMjEuNjQgMjM4LjUwMiAxMzIwLjc2IDIzNC44MjggMTMyMC43NiAyMzAuNzc1QzEzMjAuNzYgMjI2LjY3MSAxMzIxLjYyIDIyMy4wMjMgMTMyMy4zNCAyMTkuODMxQzEzMjUuMTEgMjE2LjYzOSAxMzI3LjUgMjE0LjEzMSAxMzMwLjQ5IDIxMi4zMDdDMTMzMy41MyAyMTAuNDMyIDEzMzYuOTIgMjA5LjQ5NSAxMzQwLjY3IDIwOS40OTVDMTM0My43MSAyMDkuNDk1IDEzNDYuMzkgMjEwLjA1MiAxMzQ4LjczIDIxMS4xNjdDMTM1MS4xMSAyMTIuMjMxIDEzNTMuMTEgMjEzLjcgMTM1NC43MyAyMTUuNTc1QzEzNTYuNCAyMTcuMzk5IDEzNTcuNjcgMjE5LjUwMiAxMzU4LjUzIDIyMS44ODNDMTM1OS40NCAyMjQuMjE0IDEzNTkuOSAyMjYuNjQ2IDEzNTkuOSAyMjkuMTc5QzEzNTkuOSAyMjkuNzM2IDEzNTkuODUgMjMwLjM3IDEzNTkuNzUgMjMxLjA3OUMxMzU5LjY5IDIzMS43MzggMTM1OS42MiAyMzIuMzcxIDEzNTkuNTIgMjMyLjk3OUgxMzI1LjkzVjIyNi44OTlIMTM1NS40MUwxMzUyLjA3IDIyOS42MzVDMTM1Mi41MyAyMjcgMTM1Mi4yNyAyMjQuNjQ0IDEzNTEuMzEgMjIyLjU2N0MxMzUwLjM1IDIyMC40OSAxMzQ4LjkzIDIxOC44NDMgMTM0Ny4wNSAyMTcuNjI3QzEzNDUuMTggMjE2LjQxMSAxMzQzLjA1IDIxNS44MDMgMTM0MC42NyAyMTUuODAzQzEzMzguMjkgMjE1LjgwMyAxMzM2LjExIDIxNi40MTEgMTMzNC4xMyAyMTcuNjI3QzEzMzIuMTYgMjE4Ljg0MyAxMzMwLjYxIDIyMC41OTEgMTMyOS41IDIyMi44NzFDMTMyOC40MyAyMjUuMSAxMzI4IDIyNy43NiAxMzI4LjIxIDIzMC44NTFDMTMyOCAyMzMuODQgMTMyOC40NiAyMzYuNDc1IDEzMjkuNTcgMjM4Ljc1NUMxMzMwLjc0IDI0MC45ODQgMTMzMi4zNiAyNDIuNzMyIDEzMzQuNDQgMjQzLjk5OUMxMzM2LjU3IDI0NS4yMTUgMTMzOC44NyAyNDUuODIzIDEzNDEuMzUgMjQ1LjgyM0MxMzQ0LjA5IDI0NS44MjMgMTM0Ni4zOSAyNDUuMTkgMTM0OC4yNyAyNDMuOTIzQzEzNTAuMTQgMjQyLjY1NiAxMzUxLjY2IDI0MS4wMzUgMTM1Mi44MyAyMzkuMDU5TDEzNTguNzYgMjQyLjA5OUMxMzU3Ljk1IDI0My45NzQgMTM1Ni42OCAyNDUuNjk2IDEzNTQuOTYgMjQ3LjI2N0MxMzUzLjI5IDI0OC43ODcgMTM1MS4yOCAyNTAuMDAzIDEzNDguOTUgMjUwLjkxNUMxMzQ2LjY3IDI1MS44MjcgMTM0NC4xMSAyNTIuMjgzIDEzNDEuMjggMjUyLjI4M1oiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMTA1Mi4xOCA0MS4zMTZDMTA1NS4zNyA0MS4zMTYgMTA1OC4xNyA0MC4zMjIgMTA2MC4xNiAzOC4zMzRDMTA2Mi4zNiAzNi4zNDYgMTA2My41NSAzMy43NjEgMTA2My41NSAzMC41OEMxMDYzLjU1IDI3LjM5OSAxMDYyLjM2IDI0LjgxNCAxMDYwLjE2IDIyLjgyNkMxMDU3Ljk3IDIwLjgzOCAxMDU1LjM3IDE5Ljg0NCAxMDUyLjE4IDE5Ljg0NEMxMDQ4Ljk4IDE5Ljg0NCAxMDQ2LjE5IDIwLjgzOCAxMDQzLjk5IDIyLjgyNkMxMDQxLjc5IDI0LjgxNCAxMDQwLjU5IDI3LjM5OSAxMDQwLjU5IDMwLjU4QzEwNDAuNTkgMzMuNzYxIDEwNDEuNzkgMzYuMzQ2IDEwNDMuOTkgMzguMzM0QzEwNDYuMTkgNDAuMzIyIDEwNDguOTggNDEuMzE2IDEwNTIuMTggNDEuMzE2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik00MzcuMzc2IDg2LjI1MkM0MzcuMzc2IDgwLjA4OCA0MzYuMTc4IDc0LjcyIDQzMy41ODMgNzAuMzQ2QzQzMS4xODcgNjUuNzczIDQyNy43OTIgNjIuMzkzIDQyMy40MDIgNTkuODA5QzQxOS4wMDggNTcuMjI0IDQxMy44MTUgNTYuMDMxIDQwNy44MjUgNTYuMDMxQzQwMS40MzcgNTYuMDMxIDM5NS40NDcgNTcuNjIyIDM4OS44NTUgNjAuNjA0QzM4NC4yNjQgNjMuNTg2IDM3OS42NzEgNjcuOTYgMzc2LjI4IDczLjkyNUMzNzIuODg1IDc5LjY5MSAzNzEuMDg2IDg2LjQ1MSAzNzEuMDg2IDk0LjYwMkMzNzEuMDg2IDEwMi43NTMgMzcyLjY4NiAxMDkuMTE2IDM3NS42NzkgMTE0Ljg4MUMzNzguNjc2IDEyMC40NDggMzgyLjg2NyAxMjQuODIyIDM4OC4yNTkgMTI3LjgwNUMzOTMuNjQ4IDEzMC43ODcgMzk5Ljg0MSAxMzIuMzc3IDQwNi44MjYgMTMyLjM3N0M0MTMuODE1IDEzMi4zNzcgNDIwLjAwNyAxMzAuNzg3IDQyNC45OTggMTI3LjgwNUM0MzAuMTg4IDEyNC42MjMgNDM0LjE4NCAxMjAuNDQ4IDQzNy4xNzcgMTE0Ljg4MUw0MzIuNzgzIDExMC45MDVDNDMwLjE4OCAxMTMuNjg4IDQyNy4zOTQgMTE2LjA3NSA0MjQuMzk3IDExNy44NjRDNDIxLjQwNCAxMTkuNjUzIDQxNy42MTEgMTIwLjQ0OCA0MTMuMjE4IDEyMC40NDhDNDA2LjgyNiAxMjAuNDQ4IDQwMS42MzYgMTE4LjI2MSAzOTcuMjQyIDExMy44ODdDMzkzLjA1MSAxMDkuNTEzIDM5MC44NTQgMTAzLjE1MSAzOTAuNDU2IDk0LjQwM0g0MzYuNzc5QzQzNi45NzggOTIuMjE2IDQzNy4zNzYgODkuNDMzIDQzNy4zNzYgODYuMjUyWk00MTguNDA4IDg1LjI1N0M0MTcuMjEgODYuODQ4IDQxNC44MTQgODcuNDQ1IDQxMS4yMiA4Ny40NDVIMzkwLjQ1NkMzOTAuODU0IDgxLjQ4IDM5MS44NTMgNzYuNzA4IDM5My40NDkgNzMuMTI5QzM5NS4yNDggNjkuNTUxIDM5Ny4yNDIgNjcuMTY1IDM5OS40MzkgNjUuNTc0QzQwMS44MzUgNjMuOTg0IDQwNC4yMzEgNjMuMTg5IDQwNi42MjcgNjMuMTg5QzQxMC40MjQgNjMuMTg5IDQxMy42MTYgNjQuNTgxIDQxNi4yMTEgNjcuNTYzQzQxOC44MDkgNzAuNTQ1IDQyMC4yMDYgNzQuMzIyIDQyMC4yMDYgNzguODk1QzQyMC4wMDcgODEuNDggNDE5LjQwNyA4My42NjcgNDE4LjQwOCA4NS4yNTdaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTU0Ny44MSA2Mi4yMDFDNTQyLjYxNyA1OC4wMjUgNTM1LjQyOSA1NS44MzkgNTI2LjI0NyA1NS44MzlDNTE3LjA2MSA1NS44MzkgNTA5Ljg3MyA1OC4wMjUgNTA0LjY4IDYyLjU5OEM0OTkuNDkgNjYuOTcyIDQ5Ni44OTUgNzIuOTM3IDQ5Ni44OTUgODAuMjkzQzQ5Ni44OTUgOTAuMDM1IDUwMC44ODcgOTYuOTk0IDUwOC44NzUgMTAwLjk3QzUwNS4wODIgMTA0LjM1IDUwMi4yODQgMTA3LjUzMSA1MDAuNDg5IDExMC41MTRDNDk4LjY5IDExMy4yOTcgNDk3Ljg5NCAxMTYuMjc5IDQ5Ny44OTQgMTE5LjA2M0M0OTcuODk0IDEyMS44NDYgNDk4LjY5IDEyNC4yMzIgNTAwLjA4NyAxMjYuMjJDNTAxLjY4NyAxMjguMjA4IDUwMy44ODQgMTI5Ljc5OSA1MDcuMDc2IDEzMC43OTNDNTAyLjI4NCAxMzMuMTc5IDQ5OC42OSAxMzUuNTY1IDQ5Ni42OTYgMTM4LjE0OUM0OTQuNDk5IDE0MC45MzMgNDkzLjUgMTQzLjkxNSA0OTMuNSAxNDcuMDk2QzQ5My41IDE1MC4yNzcgNDk0LjQ5OSAxNTMuNDU4IDQ5Ni40OTMgMTU2LjA0M0M0OTguNjkgMTU4LjgyNyA1MDIuMDg1IDE2MC44MTQgNTA2LjY3OCAxNjIuNjA0QzUxMS40NyAxNjQuMTk0IDUxNy42NTggMTY0Ljk5IDUyNS40NDcgMTY0Ljk5QzUzNC40MzQgMTY0Ljk5IDU0MS44MjEgMTYzLjc5NyA1NDcuODEgMTYxLjIxMkM1NTMuOCAxNTguNjI4IDU1OC4zOTMgMTU1LjQ0NyA1NjEuMzg2IDE1MS4yNzFDNTY0LjU4MiAxNDcuMDk2IDU2NS45NzkgMTQyLjcyMiA1NjUuOTc5IDEzNy45NUM1NjUuOTc5IDEzMS41ODggNTYzLjc4MiAxMjYuNjE4IDU1OS41OTEgMTIyLjg0QzU1NS4zOTYgMTE5LjA2MyA1NDguNDA4IDExNy4yNzMgNTM4LjQyNiAxMTcuMjczSDUxOS40NTdDNTE2LjA2MiAxMTcuMjczIDUxMy44NjUgMTE2LjY3NyA1MTIuNDY4IDExNS42ODNDNTExLjI3IDExNC40OSA1MTAuNjcgMTEzLjA5OCA1MTAuNjcgMTExLjExQzUxMC42NyAxMDguMTI4IDUxMS42NjkgMTA1LjM0NCA1MTMuNDY3IDEwMi43NkM1MTcuMjYgMTAzLjk1MyA1MjEuNDU1IDEwNC4zNSA1MjYuMDQ0IDEwNC4zNUM1MzUuMjMgMTA0LjM1IDU0Mi42MTcgMTAyLjE2MyA1NDcuNjExIDk3Ljc4OUM1NTIuODAxIDkzLjIxNyA1NTUuMzk2IDg3LjI1MiA1NTUuMzk2IDgwLjA5NEM1NTUuMzk2IDc1LjEyNCA1NTQuMzk3IDcwLjk0OSA1NTIuMjA0IDY3LjM3SDU2Ni43NzlWNTYuODMzTDU2NC41ODIgNTUuMjQyTDU0Ny44MSA2Mi4yMDFaTTUxMS4wNzEgMTMyLjc4MUM1MTQuMDY1IDEzMy4zNzggNTE3LjI2IDEzMy43NzUgNTIxLjA1MyAxMzMuNzc1SDUzNy44MjVDNTQyLjYxNyAxMzMuNzc1IDU0Ni4wMTIgMTM0Ljc2OSA1NDguMDA5IDEzNi43NThDNTUwLjAwNyAxMzguNzQ2IDU1MS4wMDYgMTQxLjEzMiA1NTEuMDA2IDE0My45MTVDNTUxLjAwNiAxNDcuNjkzIDU0OS4wMDggMTUwLjg3NCA1NDQuODE0IDE1My40NThDNTQwLjgyMiAxNTYuMDQzIDUzNC44MzIgMTU3LjQzNSA1MjYuODQ0IDE1Ny40MzVDNTIwLjQ1NiAxNTcuNDM1IDUxNS42NjQgMTU2LjQ0MSA1MTIuMjY5IDE1NC4yNTRDNTA4Ljg3NSAxNTIuMDY3IDUwNy4wNzYgMTQ4LjY4NyA1MDcuMDc2IDE0NC4xMTRDNTA2Ljg3NyAxNDAuMzM2IDUwOC4yNzQgMTM2LjU1OSA1MTEuMDcxIDEzMi43ODFaTTUzNS42MzIgOTMuMjE3QzUzMy40MzUgOTYuNTk2IDUzMC4yMzkgOTguMTg3IDUyNi4wNDQgOTguMTg3QzUyMS44NTMgOTguMTg3IDUxOC44NTYgOTYuNTk2IDUxNi44NjIgOTMuNDE1QzUxNC42NjUgOTAuMjM0IDUxMy42NjYgODUuODYgNTEzLjY2NiA4MC40OTJDNTEzLjY2NiA3NS4xMjQgNTE0Ljg2NCA3MC43NSA1MTcuMDYxIDY3LjU2OUM1MTkuNDU3IDY0LjE4OSA1MjIuNjUzIDYyLjU5OCA1MjYuNjQ1IDYyLjU5OEM1MzAuNjM3IDYyLjU5OCA1MzMuODMzIDY0LjE4OSA1MzUuODMxIDY3LjM3QzUzOC4wMjggNzAuNTUxIDUzOS4yMjYgNzQuNzI2IDUzOS4yMjYgODAuMDk0QzUzOS4wMjMgODUuNDYzIDUzOC4wMjggOTAuMDM1IDUzNS42MzIgOTMuMjE3WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik02NDcuNjI1IDExMC4xMDNWODIuODY1QzY0Ny42MjUgNzMuNTIgNjQ1LjgzIDY2Ljc2IDY0Mi4yMzYgNjIuMzg3QzYzOC42NDIgNTguMDEzIDYzMy40NDggNTUuODI1IDYyNy4wNiA1NS44MjVDNjE3LjY3NiA1NS44MjUgNjA4Ljg5MiA2MC4yIDYwMS4zMDIgNjkuMTQ3VjQyLjMwNkw2MDEuOTAzIDIxLjAzMkw1OTkuNzA2IDE5LjY0MUw1NzIuNzUgMjYuNFYzMi4zNjVMNTgzLjczMSAzMy45NTZWMTA5LjkwNEM1ODMuNzMxIDExNC4yNzggNTgzLjczMSAxMTguMjU0IDU4My41MzIgMTIyLjAzMkw1NzMuNTUgMTI0LjAyVjEzMC4xODRINjEwLjg4NlYxMjQuMDJMNjAxLjkwMyAxMjIuMjMxQzYwMS43IDExOC40NTMgNjAxLjcgMTE0LjI3OCA2MDEuNyAxMTAuMTAzVjc3LjI5OEM2MDcuNjk0IDcxLjUzMiA2MTMuNjg0IDY4Ljc0OSA2MTkuMjcyIDY4Ljc0OUM2MjMuMDY4IDY4Ljc0OSA2MjUuODYyIDY5Ljk0MiA2MjcuMjYgNzIuMTI5QzYyOC44NTYgNzQuMzE2IDYyOS42NTUgNzguNDkxIDYyOS42NTUgODQuMjU3VjExMC4xMDNDNjI5LjY1NSAxMTQuMjc4IDYyOS42NTUgMTE4LjI1NCA2MjkuNDU2IDEyMi4wMzJMNjE5Ljg3MyAxMjQuMDJWMTMwLjE4NEg2NTcuMDFWMTI0LjAyTDY0Ny44MjggMTIyLjIzMUM2NDcuNjI1IDExOC40NTMgNjQ3LjYyNSAxMTQuNDc3IDY0Ny42MjUgMTEwLjEwM1oiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMzc2LjI5NyAzMC4zODNIMzQyLjk1MVYzNy4zNDJMMzU1LjMzIDM5LjEzMUwzMzYuOTYxIDEwNC45NEwzMTYuNzk0IDM4LjkzMkwzMzAuOTcxIDM3LjM0MlYzMC4zODNIMjg3Ljg0MlYzNy4zNDJMMzAxLjAyIDM4LjkzMkwyODAuMjU0IDEwNC4xNDVMMjYzLjA4MiAzOC45MzJMMjc1LjY2MiAzNy4zNDJWMzAuMzgzSDIzMS43MzRWMzcuMzQyTDI0Mi43MTYgMzguNTM0TDI2OS44NzEgMTMwLjU4N0gyODAuMjU0TDMwMy4wMTcgNTcuMjIzTDMyNi45NzcgMTMwLjU4N0gzMzcuMzZMMzYzLjUxNyAzOS4xMzFMMzc1LjY5NiAzNy4xNDNWMzAuMzgzSDM3Ni4yOTdaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTQ2Ny4xMjggNDEuOTE4QzQ3MC4zMjEgNDEuOTE4IDQ3My4xMTggNDAuOTI0IDQ3NS4xMTIgMzguOTM1QzQ3Ny4zMDkgMzYuOTQ3IDQ3OC41MDcgMzQuMzYzIDQ3OC41MDcgMzEuMTgyQzQ3OC41MDcgMjggNDc3LjMwOSAyNS40MTYgNDc1LjExMiAyMy40MjhDNDcyLjkxNiAyMS40MzkgNDcwLjMyMSAyMC40NDUgNDY3LjEyOCAyMC40NDVDNDYzLjkzMyAyMC40NDUgNDYxLjEzNSAyMS40MzkgNDU4Ljk0MiAyMy40MjhDNDU2Ljc0NSAyNS40MTYgNDU1LjU0NyAyOCA0NTUuNTQ3IDMxLjE4MkM0NTUuNTQ3IDM0LjM2MyA0NTYuNzQ1IDM2Ljk0NyA0NTguOTQyIDM4LjkzNUM0NjEuMTM1IDQwLjkyNCA0NjMuOTMzIDQxLjkxOCA0NjcuMTI4IDQxLjkxOFoiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNNDc2LjExNCAxMDkuOTA2Vjc4LjQ5M0w0NzYuNTEyIDU3LjIyTDQ3NC4xMTYgNTUuNjI5TDQ0Ni45NjEgNjUuMTcyVjcwLjkzOEw0NTcuNzQ2IDcyLjMzQzQ1Ny45NDUgNzUuMzEyIDQ1OC4xNDQgNzguMjk0IDQ1OC4xNDQgODEuMDc4QzQ1OC4zNDMgODMuODYxIDQ1OC4zNDMgODcuMjQxIDQ1OC4zNDMgOTEuMjE4VjEwOS43MDhDNDU4LjM0MyAxMTQuMDgyIDQ1OC4zNDMgMTE4LjA1OCA0NTguMTQ0IDEyMS44MzZMNDQ4LjE1OSAxMjMuODI0VjEyOS45ODdINDg1LjY5OFYxMjMuODI0TDQ3Ni41MTIgMTIyLjAzNEM0NzYuMzEzIDExOC4yNTcgNDc2LjExNCAxMTQuMjggNDc2LjExNCAxMDkuOTA2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xMTQ0LjIzIDEyMi4yNDRDMTE0MS4yMyAxMjIuMjQ0IDExMzkuODMgMTIwLjA1NyAxMTM5LjgzIDExNS40ODRWODIuNjhDMTEzOS44MyA3Mi45MzggMTEzNy44MyA2NS43OCAxMTMzLjg0IDYxLjgwNEMxMTI5Ljg1IDU3LjYyOSAxMTIzLjQ2IDU1LjQ0MSAxMTE0LjY4IDU1LjQ0MUMxMTA1Ljg5IDU1LjQ0MSAxMDk4LjEgNTcuMjMxIDEwOTIuNTEgNjAuODFDMTA4Ni45MiA2NC4zODggMTA4My43MyA2OS4xNiAxMDgyLjkzIDc1LjMyM0MxMDgzLjczIDc5Ljg5NiAxMDg2LjUyIDgyLjA4MyAxMDkxLjMxIDgyLjA4M0MxMDkzLjkxIDgyLjA4MyAxMDk1LjkxIDgxLjI4OCAxMDk3LjcgNzkuNDk5QzEwOTkuNSA3Ny43MDkgMTEwMC41IDc1LjEyNCAxMTAwLjkgNzEuNTQ2TDExMDIuNyA2My4xOTVDMTEwMy44OSA2Mi45OTYgMTEwNC44OSA2Mi43OTggMTEwNS44OSA2Mi43OThDMTEwNy4wOSA2Mi41OTkgMTEwOC4wOCA2Mi41OTkgMTEwOC44OCA2Mi41OTlDMTExMy44OCA2Mi41OTkgMTExNy4yNyA2My43OTIgMTExOS4wNyA2Ni4zNzZDMTEyMS4wNiA2OC43NjIgMTEyMi4wNiA3My41MzQgMTEyMi4wNiA4MC40OTNWODQuNjY4QzExMTkuNDcgODUuNDYzIDExMTYuODcgODYuMDU5IDExMTQuMjcgODYuODU1QzExMTEuNjggODcuNjUgMTEwOS40OCA4OC4yNDYgMTEwNy40OSA4OS4wNDJDMTEwMC4zIDkxLjQyOCAxMDk0LjcxIDkzLjYxNSAxMDkwLjcyIDk2LjE5OUMxMDg2LjkyIDk4LjU4NSAxMDg0LjEzIDEwMS4xNyAxMDgyLjczIDEwMy45NTNDMTA4MS4xMyAxMDYuNzM2IDEwODAuNTMgMTA5LjcxOSAxMDgwLjUzIDExMi45QzEwODAuNTMgMTE5LjA2MyAxMDgyLjUzIDEyMy44MzUgMTA4Ni4zMiAxMjcuMDE2QzEwOTAuMzEgMTMwLjE5NyAxMDk1LjExIDEzMS43ODggMTEwMC43IDEzMS43ODhDMTEwNS40OSAxMzEuNzg4IDExMDkuNDggMTMwLjc5NCAxMTEyLjQ4IDEyOS4wMDRDMTExNS40NyAxMjcuMDE2IDExMTguODcgMTI0LjAzNCAxMTIyLjY2IDEyMC4yNTZDMTEyMy42NiAxMjMuODM1IDExMjUuMjYgMTI2LjYxOCAxMTI3Ljg1IDEyOC42MDZDMTEzMC40NSAxMzAuNTk1IDExMzMuNjQgMTMxLjU4OSAxMTM3LjY0IDEzMS41ODlDMTE0MS4yMyAxMzEuNTg5IDExNDQuMjMgMTMwLjc5NCAxMTQ2LjYyIDEyOS40MDJDMTE0OS4yMiAxMjcuODExIDExNTEuMjIgMTI1LjQyNSAxMTUzLjIxIDEyMi4wNDVMMTE0OS44MiAxMTkuMDYzQzExNDcuODIgMTIxLjA1MSAxMTQ2LjAyIDEyMi4yNDQgMTE0NC4yMyAxMjIuMjQ0Wk0xMTIxLjg2IDExNC40OUMxMTE4LjI3IDExNy4wNzUgMTExNS40NyAxMTguNjY2IDExMTMuODggMTE5LjQ2MUMxMTEyLjA4IDEyMC4yNTYgMTExMC40OCAxMjAuNjU0IDExMDguNjkgMTIwLjY1NEMxMTA1LjY5IDEyMC42NTQgMTEwMy4wOSAxMTkuODU5IDExMDAuOSAxMTguMDY5QzEwOTguOSAxMTYuMjggMTA5Ny45IDExMy4yOTggMTA5Ny45IDEwOS41MkMxMDk3LjkgMTA2LjUzOCAxMDk4LjkgMTAzLjc1NCAxMTAwLjcgMTAxLjE3QzExMDIuNyA5OC41ODUgMTEwNi4wOSA5Ni4xOTkgMTExMS4wOCA5NC4yMTFDMTExMi40OCA5My42MTUgMTExMy44OCA5My4yMTcgMTExNS44NyA5Mi42MkMxMTE3Ljg3IDkyLjAyNCAxMTE5Ljg3IDkxLjQyOCAxMTIxLjg2IDkwLjYzMlYxMTQuNDlaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTExOTQuOTIgODUuODYxTDExODguOTMgODQuMDcxQzExODMuNzMgODIuMjgyIDExODAuMzQgODAuNjkxIDExNzguMzQgNzkuMTAxQzExNzYuNTQgNzcuMzExIDExNzUuNTQgNzUuMTI0IDExNzUuNTQgNzIuNTRDMTE3NS41NCA2OS41NTcgMTE3Ni43NCA2Ny4zNyAxMTc4Ljk0IDY1LjU4MUMxMTgxLjE0IDYzLjc5MiAxMTg0LjMzIDYyLjk5NiAxMTg4LjMyIDYyLjk5NkMxMTkxLjcyIDYyLjk5NiAxMTk0LjkyIDYzLjU5MyAxMTk3LjcxIDY0Ljc4NkwxMjAwLjUxIDc3LjUxSDEyMTAuNDlMMTIxMS4yOSA2MS42MDVDMTIwNy42OSA1OS42MTYgMTIwNC4xIDU4LjAyNiAxMjAwLjUxIDU3LjAzMkMxMTk2LjkxIDU1LjgzOSAxMTkzLjEyIDU1LjQ0MSAxMTg4LjczIDU1LjQ0MUMxMTgyLjUzIDU1LjQ0MSAxMTc3LjM0IDU2LjQzNSAxMTcyLjk1IDU4LjYyMkMxMTY4Ljc2IDYwLjYxMSAxMTY1LjU2IDYzLjM5NCAxMTYzLjM3IDY2Ljk3M0MxMTYxLjE3IDcwLjM1MyAxMTU5Ljk3IDc0LjEzIDExNTkuOTcgNzguNTA0QzExNTkuOTcgODMuODczIDExNjEuNTcgODguMjQ2IDExNjQuNzYgOTEuODI1QzExNjguMTYgOTUuNDA0IDExNzIuNTUgOTcuOTg5IDExNzguMTQgOTkuNzc4TDExODUuNzMgMTAyLjM2M0MxMTkwLjUyIDEwMy45NTMgMTE5My45MiAxMDUuNzQzIDExOTUuOTEgMTA3LjUzMkMxMTk3LjkxIDEwOS4zMjEgMTE5OC45MSAxMTEuNTA4IDExOTguOTEgMTE0LjI5MUMxMTk4LjkxIDExNy40NzMgMTE5Ny43MSAxMjAuMDU3IDExOTUuMTEgMTIxLjg0N0MxMTkyLjUyIDEyMy42MzYgMTE4OC43MyAxMjQuNjMgMTE4My41MyAxMjQuNjNDMTE3OS4zNCAxMjQuNjMgMTE3NS4zNSAxMjMuODM1IDExNzEuNzUgMTIyLjQ0M0wxMTY4Ljk2IDEwOC41MjZIMTE1OC43N0wxMTU4Ljk3IDEyNi4wMjJDMTE2Mi43NyAxMjguMjA5IDExNjYuNTYgMTI5LjYwMSAxMTcwLjU1IDEzMC41OTVDMTE3NC41NSAxMzEuNzg4IDExNzguNzQgMTMyLjE4NSAxMTgzLjMzIDEzMi4xODVDMTE5My41MiAxMzIuMTg1IDEyMDEuMyAxMjkuOTk4IDEyMDYuNyAxMjUuNjI0QzEyMTIuMjggMTIxLjI1IDEyMTUuMDggMTE1LjY4MyAxMjE1LjA4IDEwOC45MjRDMTIxNS4wOCAxMDMuNzU0IDEyMTMuNDkgOTkuMTgxIDEyMTAuNDkgOTUuNjAzQzEyMDcuNDkgOTEuNDI4IDEyMDIuMyA4OC4yNDYgMTE5NC45MiA4NS44NjFaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTEyOTIuMTcgODUuNjYyQzEyOTIuMTcgNzkuNDk5IDEyOTAuOTcgNzQuMTMgMTI4OC4zNyA2OS43NTZDMTI4NS45OCA2NS4xODQgMTI4Mi41OCA2MS44MDQgMTI3OC4xOSA1OS4yMTlDMTI3My44IDU2LjYzNCAxMjY4LjYgNTUuNDQxIDEyNjIuNjEgNTUuNDQxQzEyNTYuMjMgNTUuNDQxIDEyNTAuMjQgNTcuMDMyIDEyNDQuNjQgNjAuMDE0QzEyMzkuMDUgNjIuOTk2IDEyMzQuNDYgNjcuMzcgMTIzMS4wNyA3My4zMzVDMTIyNy42NyA3OS4xMDEgMTIyNS44OCA4NS44NjEgMTIyNS44OCA5NC4wMTJDMTIyNS44OCAxMDEuOTY1IDEyMjcuNDcgMTA4LjUyNiAxMjMwLjQ3IDExNC4yOTFDMTIzMy40NiAxMTkuODU5IDEyMzcuNjYgMTI0LjIzMyAxMjQzLjA0IDEyNy4yMTVDMTI0OC40NCAxMzAuMTk3IDEyNTQuNjMgMTMxLjc4OCAxMjYxLjYyIDEzMS43ODhDMTI2OC42IDEzMS43ODggMTI3NC43OSAxMzAuMTk3IDEyNzkuNzkgMTI3LjIxNUMxMjg0Ljk4IDEyNC4wMzQgMTI4OC45NyAxMTkuODU5IDEyOTEuOTcgMTE0LjI5MUwxMjg3LjU3IDExMC4zMTVDMTI4NC45OCAxMTMuMDk5IDEyODIuMTggMTE1LjQ4NSAxMjc5LjE5IDExNy4yNzRDMTI3Ni4xOSAxMTkuMDYzIDEyNzIuNCAxMTkuODU5IDEyNjguMDEgMTE5Ljg1OUMxMjYxLjYyIDExOS44NTkgMTI1Ni40MyAxMTcuNjcxIDEyNTIuMDMgMTEzLjI5OEMxMjQ3Ljg0IDEwOC45MjQgMTI0NS42NCAxMDIuNTYxIDEyNDUuMjQgOTMuODEzSDEyOTEuNTdDMTI5MS45NyA5MS42MjYgMTI5Mi4xNyA4OC44NDMgMTI5Mi4xNyA4NS42NjJaTTEyNzMuMiA4NC40NjlDMTI3MiA4Ni4wNTkgMTI2OS42IDg2LjY1NiAxMjY2LjAxIDg2LjY1NkgxMjQ1LjI0QzEyNDUuNjQgODAuNjkxIDEyNDYuNjQgNzUuOTIgMTI0OC4yNCA3Mi4zNDFDMTI1MC4wMyA2OC43NjIgMTI1Mi4wMyA2Ni4zNzYgMTI1NC4yMyA2NC43ODZDMTI1Ni42MiA2My4xOTUgMTI1OS4wMiA2Mi40IDEyNjEuNDIgNjIuNEMxMjY1LjIxIDYyLjQgMTI2OC40IDYzLjc5MiAxMjcxIDY2Ljc3NEMxMjczLjU5IDY5Ljc1NiAxMjc1IDczLjUzNCAxMjc1IDc4LjEwN0MxMjc1IDgwLjg5IDEyNzQuMzkgODMuMDc3IDEyNzMuMiA4NC40NjlaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTY5OS4xNTYgMTIyLjQ0MkM2OTYuNzYgMTIyLjQ0MiA2OTQuNzYyIDEyMS42NDYgNjkzLjE2NiAxMTkuODU3QzY5MS43NjkgMTE4LjA2OCA2OTAuOTY5IDExNS40ODMgNjkwLjk2OSAxMTEuNzA2VjY3LjM2OUg3MDkuMzQxVjU4LjAyNEg2OTEuMTY4TDY5MS43NjkgMzcuMzQ4SDY3OS41ODdMNjczLjggNTguMDI0TDY2MS42MTcgNTkuNjE1VjY3LjM2OUg2NzIuODAxVjk5LjM3OUM2NzIuODAxIDEwMi4zNjEgNjcyLjgwMSAxMDQuNzQ3IDY3Mi41OTggMTA2LjkzNFYxMTMuNDk1QzY3Mi41OTggMTIwLjA1NiA2NzQuMzk3IDEyNS4wMjYgNjc3Ljc5MiAxMjguMDA4QzY4MS4xODYgMTMwLjk5MSA2ODUuOTc4IDEzMi41ODEgNjkxLjk2OCAxMzIuNTgxQzY5Ni43NiAxMzIuNTgxIDcwMC43NTIgMTMxLjc4NiA3MDQuMTQ3IDEyOS45OTdDNzA3LjU0MiAxMjguMjA3IDcxMC4xMzcgMTI1LjgyMiA3MTEuOTM2IDEyMi42NDFMNzA4LjM0MiAxMTguODYzQzcwNS4xNDYgMTIxLjA1IDcwMS45NSAxMjIuMjQzIDY5OS4xNTYgMTIyLjQ0MloiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNMTM1NS42NiA5NS4wMDZDMTM1Mi40NiA5MS4yMjggMTM0Ny4yNyA4OC4yNDYgMTMzOS44OCA4NS42NjFMMTMzMy44OSA4My44NzJDMTMyOC43IDgyLjA4MyAxMzI1LjMxIDgwLjQ5MiAxMzIzLjMxIDc4LjkwMUMxMzIxLjUxIDc3LjExMiAxMzIwLjUxIDc0LjkyNSAxMzIwLjUxIDcyLjM0QzEzMjAuNTEgNjkuMzU4IDEzMjEuNzEgNjcuMTcxIDEzMjMuOTEgNjUuMzgyQzEzMjYuMTEgNjMuNTkzIDEzMjkuMyA2Mi43OTcgMTMzMy4yOSA2Mi43OTdDMTMzNi42OSA2Mi43OTcgMTMzOS44OCA2My4zOTQgMTM0Mi42OCA2NC41ODZMMTM0NS40NyA3Ny4zMTFIMTM1NS40NkwxMzU2LjI1IDYxLjQwNUMxMzUyLjY2IDU5LjQxNyAxMzQ5LjA3IDU3LjgyNyAxMzQ1LjQ3IDU2LjgzM0MxMzQxLjg4IDU1LjY0IDEzMzguMDkgNTUuMjQyIDEzMzMuNjkgNTUuMjQyQzEzMjcuNSA1NS4yNDIgMTMyMi4zMSA1Ni4yMzYgMTMxNy45MiA1OC40MjNDMTMxMy43MiA2MC40MTEgMTMxMC41MyA2My4xOTUgMTMwOC4zNCA2Ni43NzRDMTMwNi4xNCA3MC4xNTQgMTMwNC45NCA3My45MzEgMTMwNC45NCA3OC4zMDVDMTMwNC45NCA4My42NzMgMTMwNi41NCA4OC4wNDcgMTMwOS43MyA5MS42MjZDMTMxMy4xMyA5NS4yMDUgMTMxNy41MiA5Ny43ODkgMTMyMy4xMSA5OS41NzlMMTMzMC43IDEwMi4xNjNDMTMzNS40OSAxMDMuNzU0IDEzMzguODkgMTA1LjU0MyAxMzQwLjg4IDEwNy4zMzNDMTM0Mi44OCAxMDkuMTIyIDEzNDMuODggMTExLjMwOSAxMzQzLjg4IDExNC4wOTJDMTM0My44OCAxMTcuMjczIDEzNDIuNjggMTE5Ljg1OCAxMzQwLjA4IDEyMS42NDdDMTMzNy40OCAxMjMuNDM3IDEzMzMuNjkgMTI0LjQzMSAxMzI4LjUgMTI0LjQzMUMxMzI0LjMxIDEyNC40MzEgMTMyMC4zMSAxMjMuNjM1IDEzMTYuNzIgMTIyLjI0NEwxMzEzLjkzIDEwOC4zMjdIMTMwMy43NEwxMzAzLjk0IDEyNS44MjNDMTMwNy43MyAxMjguMDEgMTMxMS41MyAxMjkuNDAxIDEzMTUuNTIgMTMwLjM5NUMxMzE5LjUxIDEzMS41ODggMTMyMy43MSAxMzEuOTg2IDEzMjguMyAxMzEuOTg2QzEzMzguNDggMTMxLjk4NiAxMzQ2LjI3IDEyOS43OTkgMTM1MS42NiAxMjUuNDI1QzEzNTcuMjUgMTIxLjA1MSAxMzYwLjA1IDExNS40ODQgMTM2MC4wNSAxMDguNzI0QzEzNjAuNDUgMTAzLjM1NiAxMzU4Ljg1IDk4Ljc4MyAxMzU1LjY2IDk1LjAwNloiIGZpbGw9IiNGREZERkQiPjwvcGF0aD48cGF0aCBkPSJNNzU0LjI1OSA4Ni40NTFMNzQ4LjI2OSA4NC42NjJDNzQzLjA3NSA4Mi44NzIgNzM5LjY4MSA4MS4yODIgNzM3LjY4NiA3OS42OTFDNzM1Ljg4OCA3Ny45MDIgNzM0Ljg4OSA3NS43MTUgNzM0Ljg4OSA3My4xM0M3MzQuODg5IDcwLjE0OCA3MzYuMDg3IDY3Ljk2MSA3MzguMjg0IDY2LjE3MkM3NDAuNDggNjQuMzgyIDc0My42NzYgNjMuNTg3IDc0Ny42NjggNjMuNTg3Qzc1MS4wNjMgNjMuNTg3IDc1NC4yNTkgNjQuMTgzIDc1Ny4wNTMgNjUuMzc2TDc1OS44NDcgNzguMUg3NjkuODMzTDc3MC42MzIgNjIuMzk0Qzc2Ny4wMzUgNjAuNDA2IDc2My40NDEgNTguODE1IDc1OS44NDcgNTcuODIxQzc1Ni4yNTMgNTYuNjI4IDc1Mi40NiA1Ni4yMyA3NDguMDY2IDU2LjIzQzc0MS44NzggNTYuMjMgNzM2LjY4OCA1Ny4yMjUgNzMyLjI5NCA1OS40MTJDNzI4LjEwMyA2MS40IDcyNC45MDcgNjQuMTgzIDcyMi43MSA2Ny43NjJDNzIwLjUxMyA3MS4xNDIgNzE5LjMxNSA3NC45MTkgNzE5LjMxNSA3OS4yOTNDNzE5LjMxNSA4NC42NjIgNzIwLjkxMSA4OS4wMzYgNzI0LjEwNyA5Mi42MTRDNzI3LjUwMiA5Ni4xOTMgNzMxLjg5NiA5OC43NzggNzM3LjQ4NCAxMDAuNTY3TDc0NS4wNzMgMTAzLjE1MkM3NDkuODY1IDEwNC43NDIgNzUzLjI2IDEwNi41MzIgNzU1LjI1OCAxMDguMzIxQzc1Ny4yNTIgMTEwLjExIDc1OC4yNTEgMTEyLjI5NyA3NTguMjUxIDExNS4wODFDNzU4LjI1MSAxMTguMjYyIDc1Ny4wNTMgMTIwLjg0NyA3NTQuNDU4IDEyMi42MzZDNzUxLjg2MyAxMjQuNDI1IDc0OC4wNjYgMTI1LjQxOSA3NDIuODc2IDEyNS40MTlDNzM4LjY4MiAxMjUuNDE5IDczNC42OSAxMjQuNjI0IDczMS4wOTYgMTIzLjIzMkw3MjguMzAyIDEwOS4zMTVINzE4LjExN0w3MTguMzE2IDEyNi44MTFDNzIyLjEwOSAxMjguOTk4IDcyNS45MDYgMTMwLjM5IDcyOS44OTggMTMxLjM4NEM3MzMuODkgMTMyLjU3NyA3MzguMDg1IDEzMi45NzQgNzQyLjY3NyAxMzIuOTc0Qzc1Mi44NTggMTMyLjk3NCA3NjAuNjQ3IDEzMC43ODcgNzY2LjA0IDEyNi40MTNDNzcxLjYyOCAxMjIuMDM5IDc3NC40MjUgMTE2LjQ3MiA3NzQuNDI1IDEwOS43MTNDNzc0LjQyNSAxMDQuNTQzIDc3Mi44MjYgOTkuOTcxIDc2OS44MzMgOTYuMzkyQzc2Ni44MzYgOTIuMDE4IDc2MS42NDYgODguODM3IDc1NC4yNTkgODYuNDUxWiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xMDYxLjE2IDEwOS4zMTdWNzcuOTAzTDEwNjEuNTYgNTYuNjNMMTA1OS4xNiA1NS4wMzlMMTAzMi4wMSA2NC41ODNWNzAuMzQ4TDEwNDIuNzkgNzEuNzRDMTA0Mi45OSA3NC43MjIgMTA0Mi45OSA3Ny43MDQgMTA0Mi45OSA4MC40ODhDMTA0My4xOSA4My4yNzIgMTA0My4xOSA4Ni42NTEgMTA0My4xOSA5MC42MjhWMTA5LjExOEMxMDQzLjE5IDExMy40OTIgMTA0My4xOSAxMTcuNDY4IDEwNDIuOTkgMTIxLjI0NkwxMDMzLjAxIDEyMy4yMzRWMTI5LjM5N0gxMDcwLjU0VjEyMy4yMzRMMTA2MS4zNiAxMjEuNDQ1QzEwNjEuMTYgMTE3LjY2NyAxMDYxLjE2IDExMy42OTEgMTA2MS4xNiAxMDkuMzE3WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik04NzMuODY3IDY5Ljk0N0w4ODUuNjQ4IDcxLjkzNUM4ODQuNDUgNzcuMzAzIDg4My4wNTMgODIuMjc0IDg4MS4yNTQgODYuODQ2Qzg3OS40NTkgOTEuMjIgODc3LjQ2MSA5NS41OTQgODc0LjY2NyAxMDAuMTY3Qzg3Mi4wNjggOTcuNTgyIDg2OS42NzIgOTQuOTk4IDg2Ny4wNzcgOTIuMjE0Qzg2NC40ODIgODkuNDMxIDg2MS44ODcgODYuNDQ5IDg1OC44OSA4My4yNjdDODU2LjI5NSA4MC40ODQgODU0LjA5OSA3OC4wOTggODUyLjEwMSA3Ni4xMUM4NTAuMTA3IDczLjkyMyA4NDguNTA3IDcyLjEzNCA4NDcuMTEgNzAuNTQzQzg1NC44OTggNjYuNzY2IDg2MC40OSA2Mi45ODggODY0LjI4MyA1OS4wMTJDODY3Ljg3NyA1NS4wMzUgODY5LjY3MiA1MC40NjIgODY5LjY3MiA0NS4yOTNDODY5LjY3MiAzOS41MjcgODY3LjQ3NSAzNC45NTUgODYzLjI4NCAzMS4zNzZDODU5LjA4OSAyNy43OTcgODUyLjkgMjYuMDA4IDg0NC45MTMgMjYuMDA4QzgzNi45MjkgMjYuMDA4IDgzMC43MzYgMjcuOTk2IDgyNS45NDQgMzEuOTcyQzgyMC45NTMgMzUuOTQ5IDgxOC41NTcgNDEuNTE2IDgxOC41NTcgNDguNDc0QzgxOC41NTcgNTIuMjUyIDgxOS4zNTcgNTYuMjI4IDgyMC43NTQgNjAuMDA2QzgyMi4xNTEgNjMuOTgyIDgyNC43NDYgNjcuOTU5IDgyOC4zNCA3Mi4zMzJDODI4LjUzOSA3Mi41MzEgODI4Ljc0MiA3Mi41MzEgODI4Ljc0MiA3Mi43M0M4MjguOTQxIDcyLjkyOSA4MjguOTQxIDcyLjkyOSA4MjkuMTQgNzMuMTI4QzgyMS4zNTIgNzYuOTA1IDgxNS41NjEgODEuMDggODExLjc2OCA4Ni4wNTFDODA3Ljk3NSA5MC44MjIgODA2LjE4IDk2LjM5IDgwNi4xOCAxMDIuNzUyQzgwNi4xOCAxMDcuNzIyIDgwNy4zNzggMTEyLjA5NiA4MDkuOTczIDExNi4yNzFDODEyLjU2OCAxMjAuMjQ4IDgxNi4xNjIgMTIzLjYyOCA4MjAuOTUzIDEyNi4wMTRDODI1Ljc0NSAxMjguMzk5IDgzMS4zMzcgMTI5LjU5MiA4MzcuNzI1IDEyOS41OTJDODQ0LjkxMyAxMjkuNTkyIDg1MC45MDMgMTI4LjM5OSA4NTUuNjk1IDEyNi4yMTJDODYwLjQ5IDEyMy44MjYgODY0LjQ4MiAxMjEuMDQzIDg2Ny42NzggMTE3Ljg2MkM4NjguNDc0IDExOC42NTcgODY5LjA3NSAxMTkuMjU0IDg2OS44NzEgMTIwLjA0OUM4NzAuNjcxIDEyMC44NDQgODcxLjQ3MSAxMjEuNDQxIDg3Mi4wNjggMTIyLjIzNkM4NzUuMDY1IDEyNS4wMTkgODc4LjA1OCAxMjcuMDA4IDg4MS4wNTUgMTI4LjAwMUM4ODQuMDQ4IDEyOS4xOTUgODg3LjY0NSAxMjkuNTkyIDg5Mi4wMzUgMTI5LjU5MkM4OTQuMjMyIDEyOS41OTIgODk2LjAzMSAxMjkuMzkzIDg5OC4wMjUgMTI5LjE5NUM5MDAuMDIzIDEyOC45OTYgOTAyLjIyIDEyOC41OTggOTA1LjIxMyAxMjcuODAzTDkwNi4yMTIgMTE5LjQ1M0w4OTEuNjM3IDExNi44NjhDODg5LjQ0IDExNC40ODIgODg3LjQ0MyAxMTIuNDk0IDg4NS40NDggMTEwLjMwN0M4ODMuNDUxIDEwOC4zMTkgODgxLjY1MiAxMDYuMzMgODc5Ljg1NyAxMDQuMzQyQzg4My40NTEgOTkuMTczIDg4Ni40NDQgOTQuMDA0IDg4OC44NDMgODguODM0Qzg5MS40MzggODMuNjY1IDg5My42MzUgNzcuNzAxIDg5NS40MyA3MS4xNEw5MDYuNDExIDY5LjM1VjYyLjc4OUg4NzQuNDY0TDg3My44NjcgNjkuOTQ3Wk04MzYuMzI4IDM1LjM1MkM4MzguNzI0IDMyLjk2NiA4NDEuNTE4IDMxLjc3NCA4NDQuOTEzIDMxLjc3NEM4NDguMzA4IDMxLjc3NCA4NTEuMTA1IDMyLjk2NiA4NTMuMjk5IDM1LjE1M0M4NTUuNDk2IDM3LjM0IDg1Ni42OTMgNDAuMzIzIDg1Ni42OTMgNDQuMjk5Qzg1Ni42OTMgNDguMDc3IDg1NS40OTYgNTEuNjU1IDg1My4yOTkgNTUuMjM0Qzg1MC45MDMgNTguODEzIDg0Ny43MTEgNjIuMzkxIDg0My43MTUgNjUuOTdDODQyLjkxOSA2NC45NzYgODQyLjExOSA2My45ODIgODQxLjUxOCA2My4xODdDODQwLjcyMiA2Mi4xOTMgODQwLjEyMSA2MS4zOTcgODM5LjMyNSA2MC40MDRDODM2LjkyOSA1Ny4yMjIgODM1LjMyOSA1NC4yNCA4MzQuNTMzIDUxLjg1NEM4MzMuNzMzIDQ5LjI3IDgzMy4zMzUgNDYuODg0IDgzMy4zMzUgNDQuNDk4QzgzMi45MzMgNDAuOTE5IDgzNC4xMzEgMzcuOTM3IDgzNi4zMjggMzUuMzUyWk04NDQuNzE0IDExOS4wNTVDODQwLjMyIDExOS4wNTUgODM2LjUyNyAxMTguMDYxIDgzMy4xMzIgMTE2LjI3MUM4MjkuOTQgMTE0LjI4MyA4MjcuMzQxIDExMS44OTcgODI1LjU0NiAxMDguNTE4QzgyMy43NDcgMTA1LjMzNiA4MjIuNzUyIDEwMS43NTggODIyLjc1MiA5Ny45OEM4MjIuNzUyIDk0LjQwMSA4MjMuNTQ4IDkxLjAyMSA4MjQuOTQ1IDg3LjQ0M0M4MjYuMzQ2IDgzLjg2NCA4MjguOTQxIDgwLjY4MyA4MzIuNzM0IDc3Ljg5OUM4MzQuNzMyIDgwLjI4NSA4MzYuOTI5IDgzLjA2OSA4MzkuMzI1IDg2LjA1MUM4NDEuOTIgODkuMDMzIDg0NC45MTMgOTIuNjEyIDg0OC4zMDggOTYuNzg3Qzg1MC41MDUgOTkuMzcyIDg1Mi43MDEgMTAyLjE1NSA4NTUuMDk3IDEwNC45MzlDODU3LjQ5MyAxMDcuNzIyIDg2MC4wODggMTEwLjUwNiA4NjIuNjgzIDExMy4yODlDODU3LjY5MiAxMTcuMDY2IDg1MS43MDMgMTE4Ljg1NiA4NDQuNzE0IDExOS4wNTVaIiBmaWxsPSIjRkRGREZEIj48L3BhdGg+PHBhdGggZD0iTTk5My4yNyA3Ni45MTNDMTAwMi4yNSA3NS4xMjMgMTAwOC42NCA3Mi4zNCAxMDEyLjIzIDY3Ljk2NkMxMDE1LjgzIDYzLjU5MiAxMDE3LjYzIDU4LjgyMSAxMDE3LjYzIDUzLjY1MUMxMDE3LjYzIDQ2LjY5MiAxMDE0LjgzIDQwLjkyNyAxMDA5LjI0IDM2LjU1M0MxMDAzLjY1IDMxLjk4IDk5NS4wNiAyOS43OTMgOTgzLjQ4IDI5Ljc5M0g5MzcuMTZWMzYuOTUxTDk0OS45NCAzOC4zNDJDOTUwLjEzIDQ0LjcwNCA5NTAuMTMgNTEuMjY1IDk1MC4xMyA1Ny42MjdWMTAyLjE2M0M5NTAuMTMgMTA4LjUyNSA5NDkuOTQgMTE0Ljg4NyA5NDkuOTQgMTIxLjI0OUw5MzcuMTYgMTIyLjY0MVYxMjkuNzk5SDk3OS4yOUM5ODcuNjcgMTI5Ljc5OSA5OTQuNjYgMTI5LjAwMyAxMDAwLjI1IDEyNy40MTNDMTAwNS44NSAxMjUuODIyIDEwMTAuNDQgMTIzLjYzNSAxMDEzLjYzIDEyMC44NTJDMTAxNy4wMyAxMTguMDY4IDEwMTkuNDIgMTE1LjA4NiAxMDIwLjgyIDExMS45MDVDMTAyMi40MiAxMDguNTI1IDEwMjMuMDIgMTA1LjM0NCAxMDIzLjAyIDEwMS45NjRDMTAyMy4wMiA5NS42MDIgMTAyMC42MiA5MC4yMzQgMTAxNi4wMyA4NS42NjFDMTAxMS40MyA4MS4wODggMTAwMy44NSA3OC4zMDUgOTkzLjI3IDc2LjkxM1pNOTY5LjcgNTYuNjMzQzk2OS45IDUwLjI3MSA5NjkuOSA0My45MDkgOTY5LjkgMzcuNTQ3SDk3Ny44OUM5ODQuNjggMzcuNTQ3IDk4OS44NyAzOC45MzggOTkzLjA3IDQxLjcyMkM5OTYuNDYgNDQuNTA2IDk5OC4yNiA0OC44OCA5OTguMjYgNTUuMDQzQzk5OC4yNiA2MS4yMDYgOTk2LjQ2IDY2LjE3NyA5OTIuODcgNjkuMzU4Qzk4OS4yNyA3Mi41MzkgOTgzLjQ4IDczLjkzMSA5NzUuNjkgNzMuOTMxSDk2OS41MUw5NjkuNyA1Ni42MzNaTTk3Ny4wOSAxMjEuODQ2SDk2OS45Qzk2OS43IDExNS40ODQgOTY5LjcgMTA5LjEyMSA5NjkuNyAxMDIuNTZWODEuNDg2SDk3Ni40OUM5ODUuNDggODEuNDg2IDk5Mi4wNyA4My4yNzUgOTk2LjI2IDg2LjY1NUMxMDAwLjQ1IDkwLjAzNSAxMDAyLjY1IDk1LjAwNSAxMDAyLjY1IDEwMS45NjRDMTAwMi42NSAxMTUuMDg2IDk5NC4yNiAxMjEuODQ2IDk3Ny4wOSAxMjEuODQ2WiIgZmlsbD0iI0ZERkRGRCI+PC9wYXRoPjxwYXRoIGQ9Ik0xNy4yNTkgMjEuNjI5QzIzLjI0OSAyMS42MjkgMjguMDQxIDE2Ljg1NyAyOC4wNDEgMTAuODkyNEMyOC4wNDEgNC45Mjc5IDIzLjI0OSAwLjE1NjE4OSAxNy4yNTkgMC4xNTYxODlDMTEuMjY4NyAwLjE1NjE4OSA2LjQ3NjU2IDQuOTI3OSA2LjQ3NjU2IDEwLjg5MjRDNi40NzY1NiAxNi44NTcgMTEuMjY4NyAyMS42MjkgMTcuMjU5IDIxLjYyOVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMjEuMDYzIDcwLjE1NUMzMC4yNDggNjcuOTY4IDM2LjAzOCA1OC44MjIgMzMuODQyIDQ5LjY3NkMzMS42NDYgNDAuNTMxIDIyLjQ2MSAzNC43NjUgMTMuMjc2IDM2Ljk1MkM0LjA5MDk3IDM5LjEzOSAtMS42OTk0MyA0OC4yODUgMC40OTY5NzIgNTcuNDNDMi42OTMyNyA2Ni43NzUgMTEuODc4MiA3Mi4zNDIgMjEuMDYzIDcwLjE1NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMjEuMDYzIDE1NS40NDhDMzAuMjQ4IDE1My4yNiAzNi4wMzggMTQ0LjExNSAzMy44NDIgMTM0Ljk2OUMzMS42NDYgMTI1LjgyNCAyMi40NjEgMTIwLjA1OCAxMy4yNzYgMTIyLjI0NUM0LjA5MDk3IDEyNC40MzIgLTEuNjk5NDMgMTMzLjU3OCAwLjQ5Njk3MiAxNDIuNzIzQzIuNjkzMjcgMTUxLjg2OSAxMS44NzgyIDE1Ny42MzUgMjEuMDYzIDE1NS40NDhaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTI3Ljg2OSA5Ni4xODVDMjcuODY5IDkwLjIyMSAyMy4wNzcgODUuNDQ5IDE3LjA4NyA4NS40NDlDMTEuMDk2OCA4NS40NDkgNi4zMDQ2OSA5MC4yMjEgNi4zMDQ2OSA5Ni4xODVDNi4zMDQ2OSAxMDIuMTUgMTEuMDk2OCAxMDYuOTIyIDE3LjA4NyAxMDYuOTIyQzIzLjA3NyAxMDYuOTIyIDI3Ljg2OSAxMDIuMTUgMjcuODY5IDk2LjE4NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNODIuOTc2OSA5NUM3My41OTE5IDk1IDY1LjgwNDkgMTAyLjU1NSA2NS44MDQ5IDExMi4wOThDNjUuODA0OSAxMjEuNDQzIDczLjM5MTkgMTI5LjE5NyA4Mi45NzY5IDEyOS4xOTdDOTIuMzYwOSAxMjkuMTk3IDEwMC4xNDggMTIxLjY0MSAxMDAuMTQ4IDExMi4wOThDOTkuOTQ3OSAxMDIuNTU1IDkyLjM2MDkgOTUgODIuOTc2OSA5NVoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNODIuOTc4MSAxNDMuOTAyQzc2Ljk4ODEgMTQzLjkwMiA3Mi4xOTUxIDE0OC42NzQgNzIuMTk1MSAxNTQuNjM5QzcyLjE5NTEgMTYwLjYwMyA3Ni45ODgxIDE2NS4zNzUgODIuOTc4MSAxNjUuMzc1Qzg4Ljk2ODEgMTY1LjM3NSA5My43NjAxIDE2MC42MDMgOTMuNzYwMSAxNTQuNjM5QzkzLjU2MDEgMTQ4LjY3NCA4OC43NjgxIDE0My45MDIgODIuOTc4MSAxNDMuOTAyWiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik04Mi45NzgxIDgwLjA4MkM4OC45NjgxIDgwLjA4MiA5My43NjAxIDc1LjMxIDkzLjc2MDEgNjkuMzQ1QzkzLjc2MDEgNjMuMzgxIDg4Ljk2ODEgNTguNjA5IDgyLjk3ODEgNTguNjA5Qzc2Ljk4ODEgNTguNjA5IDcyLjE5NTEgNjMuMzgxIDcyLjE5NTEgNjkuMzQ1QzcyLjE5NTEgNzUuMzEgNzYuOTg4MSA4MC4wODIgODIuOTc4MSA4MC4wODJaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTg0LjU2MDEgMzcuMzQ1QzkwLjM1MDEgMzYuMzUxIDk0LjM0MzEgMzAuOTgzIDkzLjM0NTEgMjUuMjE3QzkyLjM0NzEgMTkuNDUxIDg2Ljk1NjEgMTUuNDc1IDgxLjE2NTEgMTYuNDY5Qzc1LjM3NTEgMTcuNDYzIDcxLjM4MTEgMjIuODMxIDcyLjM4MDEgMjguNTk3QzczLjM3ODEgMzQuMzYzIDc4Ljc2OTEgMzguMTQgODQuNTYwMSAzNy4zNDVaIiBmaWxsPSIjRkNCQzMyIj48L3BhdGg+PHBhdGggZD0iTTE2MC42NDkgNjUuNTc5QzE2Ny4yMzggNTkuMDE4IDE2Ny4yMzggNDguMDgzIDE2MC42NDkgNDEuNTIyQzE1NC4wNiAzNC45NjEgMTQzLjA3OCAzNC45NjEgMTM2LjQ4OSA0MS41MjJDMTI5LjkgNDguMDgzIDEyOS45IDU5LjAxOCAxMzYuNDg5IDY1LjU3OUMxNDMuMDc4IDcyLjMzOSAxNTQuMDYgNzIuMzM5IDE2MC42NDkgNjUuNTc5WiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik0xNDguNjY1IDIxLjYyOUMxNTQuNjU1IDIxLjYyOSAxNTkuNDQ3IDE2Ljg1NyAxNTkuNDQ3IDEwLjg5MjRDMTU5LjQ0NyA0LjkyNzkgMTU0LjY1NSAwLjE1NjE4OSAxNDguNjY1IDAuMTU2MTg5QzE0Mi42NzUgMC4xNTYxODkgMTM3Ljg4MyA0LjkyNzkgMTM3Ljg4MyAxMC44OTI0QzEzNy44ODMgMTYuODU3IDE0Mi42NzUgMjEuNjI5IDE0OC42NjUgMjEuNjI5WiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjxwYXRoIGQ9Ik0xNDguNjY1IDg1LjY0OEMxNDIuNjc1IDg1LjY0OCAxMzcuODgzIDkwLjQyIDEzNy44ODMgOTYuMzg1QzEzNy44ODMgMTAyLjM0OSAxNDIuNjc1IDEwNy4xMjEgMTQ4LjY2NSAxMDcuMTIxQzE1NC42NTUgMTA3LjEyMSAxNTkuNDQ3IDEwMi4zNDkgMTU5LjQ0NyA5Ni4zODVDMTU5LjI0OCA5MC40MiAxNTQuNDU1IDg1LjY0OCAxNDguNjY1IDg1LjY0OFoiIGZpbGw9IiNGQ0JDMzIiPjwvcGF0aD48cGF0aCBkPSJNMTQ4LjY2NSAxMjguMjAzQzE0Mi42NzUgMTI4LjIwMyAxMzcuODgzIDEzMi45NzUgMTM3Ljg4MyAxMzguOTM5QzEzNy44ODMgMTQ0LjkwNCAxNDIuNjc1IDE0OS42NzUgMTQ4LjY2NSAxNDkuNjc1QzE1NC42NTUgMTQ5LjY3NSAxNTkuNDQ3IDE0NC45MDQgMTU5LjQ0NyAxMzguOTM5QzE1OS4yNDggMTMyLjk3NSAxNTQuNDU1IDEyOC4yMDMgMTQ4LjY2NSAxMjguMjAzWiIgZmlsbD0iI0ZDQkMzMiI+PC9wYXRoPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzdfMiI+PHJlY3Qgd2lkdGg9IjEzNjAiIGhlaWdodD0iMjY5IiBmaWxsPSJ3aGl0ZSI+PC9yZWN0PjwvY2xpcFBhdGg+PC9kZWZzPjwvc3ZnPg==" width="148" height="29" alt="Weights &amp; Biases by CoreWeave">
      <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 72 72" fill="none" aria-hidden="true" focusable="false">
    <rect width="72" height="72" rx="36" fill="#EDE8FF" fill-opacity=".12"/>
    <path d="M36 17 54 27 36 37 18 27 36 17Z" fill="#FFCC33"/>
    <path d="M18 27 36 37V56L18 46V27Z" fill="#FFAD33"/>
    <path d="M54 27 36 37V56L54 46V27Z" fill="#FCBC32"/>
    <path d="M27 22 45 32M36 37V56" stroke="#20242B" stroke-width="2" stroke-linejoin="round" opacity=".4"/>
    </svg>
      <span class="cw-wb-title">Sandboxes</span>
      <span class="cw-wb-description">Isolated environments<br>for agent code</span>
      <span class="cw-wb-docs">Read docs <span aria-hidden="true">↗</span></span>
    </a>""")
    return (wandb_sandboxes_card,)


@app.cell(hide_code=True)
def sandbox_teaching(wandb_sandboxes_card):
    mo.hstack([
        mo.md("""
        ### Give inference a Sandbox tool

        The model sees **run_python(code)**: submit a complete Python program defining
        **solve(world)**, and receive execution results plus a Wanderland verdict.

        The three visible code cells below show the real implementation:

        1. **agent_tool** declares the tool's name, description, and one string argument.
        2. **agent_request** passes it to W&B Inference with **tools=[RUN_PYTHON_TOOL]**.
        3. **sandbox_function** creates a Sandbox, waits for readiness, uploads the program
           and world, runs Python, reads the plan, and stops the Sandbox.

        **agent_loop** connects them: it reads the model's tool call, invokes
        **run_in_sandbox**, checks the plan with Wanderland, and sends feedback back as
        a **tool** message.

        The model gets Python 3.11 instructions and knows each call uses a fresh Sandbox.
        Credentials, resource settings, Sandbox SDK calls, and Weave instrumentation are
        handled by the notebook.
        """),
        wandb_sandboxes_card,
    ], align="start", widths=[0.72, 0.28], gap=1.5)
    return


@app.cell
def agent_tool():
    # 1. The model sees this tool contract: one Python source string.
    RUN_PYTHON_TOOL = {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Run a complete Python solve(world) program in a fresh Sandbox and check its returned plan in Wanderland.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string", 
                        "description": "Complete Python source with imports and def solve(world), returning a list of action names."}
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        },
    }
    return (RUN_PYTHON_TOOL,)


@app.cell
def agent_request(
    RUN_PYTHON_TOOL,
    THINKING_ALWAYS_ON_MODELS,
    inference_client,
    inference_options,
):
    # 2. Make that tool available to the model through W&B Inference.
    def request_agent_stream(model_name, messages, thinking, seed):
        options = inference_options(model_name, thinking, task="agent")
        return inference_client.chat.completions.create(
            model=model_name, messages=messages, tools=[RUN_PYTHON_TOOL],
            tool_choice="auto", parallel_tool_calls=False,
            seed=seed, max_tokens=6144 if thinking is True or model_name in THINKING_ALWAYS_ON_MODELS else 4096,
            **options, stream=True,
            stream_options={"include_usage": True},
        )


    return (request_agent_stream,)


@app.cell
def sandbox_config():
    SANDBOX_DEFAULTS = SandboxDefaults(
        container_image="python:3.11",
        tags=("coreweave-hacks-demo", "gridworld"),
        environment_variables={"PYTHONUNBUFFERED": "1"},
        max_lifetime_seconds=120,
        request_timeout_seconds=30,
        resources=ResourceOptions(
            requests={"cpu": "250m", "memory": "256Mi"},
            limits={"cpu": "1", "memory": "512Mi"},
        ),
    )
    SANDBOX_RUNNER = """import json
    from solution import solve

    with open("/tmp/world.json") as source:
        world = json.load(source)
    plan = solve(world)
    with open("/tmp/plan.json", "w") as destination:
        json.dump(plan, destination)
    """
    return SANDBOX_DEFAULTS, SANDBOX_RUNNER


@app.cell
def sandbox_function(SANDBOX_DEFAULTS, SANDBOX_RUNNER):
    # 3. Our notebook implements the tool with Serverless Sandboxes.
    @weave.op(name="run_gridworld_solver")
    def run_in_sandbox(code: str, world: dict) -> dict:
        started = time.monotonic()
        sandbox = None
        result = {"status": "error", "plan": None, "error": "", "cleanup_warning": ""}
        try:
            # Parse for feedback; execution happens only in the remote Sandbox.
            tree = ast.parse(code)
            if not any(isinstance(node, ast.FunctionDef) and node.name == "solve" for node in tree.body):
                raise ValueError("Define a top-level function solve(world) before running.")
            sandbox = Sandbox.run(defaults=SANDBOX_DEFAULTS)
            result["sandbox_id"] = sandbox.sandbox_id
            # Creation is asynchronous: wait before writing files or executing code.
            sandbox.wait(timeout=60)
            # Upload the model's code, the world, and the runner.
            sandbox.write_file("/tmp/solution.py", code.encode()).result()
            sandbox.write_file("/tmp/world.json", json.dumps(world).encode()).result()
            sandbox.write_file("/tmp/run.py", SANDBOX_RUNNER.encode()).result()
            # Execute remotely and read the returned plan.
            completion = sandbox.exec(
                ["python", "/tmp/run.py"], timeout_seconds=10, check=True
            ).result()
            result["stdout"] = (completion.stdout or "")[-2000:]
            result["stderr"] = (completion.stderr or "")[-2000:]
            result["plan"] = json.loads(sandbox.read_file("/tmp/plan.json").result().decode())
            result["status"] = "completed"
        except SandboxCommandTimeoutError:
            result["error"] = "The solver exceeded its 10-second execution limit."
        except SandboxExecutionError as error:
            result["error"] = "Python failed inside the Sandbox: " + str(error)[-2000:]
            if error.exec_result is not None:
                result["stdout"] = (error.exec_result.stdout or "")[-2000:]
                result["stderr"] = (error.exec_result.stderr or "")[-2000:]
        except SandboxError as error:
            result["error"] = "Sandbox request failed: " + str(error)[-2000:]
        except Exception as error:
            result["error"] = f"{type(error).__name__}: {error}"[-2000:]
        finally:
            # Stop the Sandbox whether execution succeeded or failed.
            if sandbox is not None:
                try:
                    sandbox.stop(missing_ok=True).result()
                except Exception as error:
                    result["cleanup_warning"] = (
                        "Could not confirm Sandbox cleanup. Its 120-second lifetime cap still applies. "
                        + str(error)[-300:]
                    )
            result["seconds"] = round(time.monotonic() - started, 2)
        return result

    return (run_in_sandbox,)


@app.cell(hide_code=True)
def agent_controls(reasoning_note, thinking_always_on, thinking_can_toggle):
    agent_button = mo.ui.run_button(label="Plan with code", kind="success")
    agent_thinking = mo.ui.switch(value=thinking_always_on, label="🧠 agent thinking", disabled=not thinking_can_toggle)
    agent_close_loop = mo.ui.switch(value=True, label="🔁 Close the loop")
    mo.vstack([
        mo.hstack([agent_button, agent_thinking, agent_close_loop], justify="start", gap=1.2),
        mo.md(reasoning_note),
        mo.md("One click writes and runs the code. With **Close the loop** on, the model gets feedback and can try again, for up to six turns."),
    ])
    return agent_button, agent_close_loop, agent_thinking


@app.cell(hide_code=True)
def agent_inference(
    RUN_PYTHON_TOOL,
    WORLD,
    build_planner_prompt,
    gen_env,
    inference_options,
    request_agent_stream,
):
    AGENT_PROMPT = build_planner_prompt(gen_env) + """

    ---

    Do NOT work the path out by hand. Use the run_python tool to find the plan:
    write a complete Python function solve(world) that searches for a solution
    and returns its action list. The tool supplies world to your function; do
    not retype the world. Use only the Python 3.11 standard library. Each call
    runs in a fresh Sandbox, so include your imports and the full function.
    Do not use network access or external files. Call the tool once per turn.

    The world below is the EXACT dictionary passed to solve(world):
    - cols and rows are ints; heading is a compass letter N/E/S/W.
    - start and goal are [x,y] lists. walls, gaps (water), lava, and gems are
      lists of [x,y] coordinates. Convert coordinates to tuples when needed.
    - objects maps "x,y" strings to records with type, color, state, and
      optional blocking. Gems are non-blocking; keys and locked doors block.
    - pickup takes the key on the tile you FACE into your one hand.
    - toggle unlocks the door you FACE while carrying its matching-color key.
      An open door is passable; you keep the key.
    - collect_gem collects the gem on the tile you STAND on.
    - Avoid lava, collect EVERY gem, and finish on the goal. Return no more
      than 200 actions, using only the world's allowed action names.

    Read the tool's execution feedback. If code fails or a plan is rejected,
    fix the program and call run_python again. A proposed plan is not a
    solution until the Sandbox has run your code and Wanderland verifies it.
    """ + "\n" + json.dumps(WORLD, indent=2)


    def preview_agent_code(content, calls):
        # Partial JSON is for display only; execution still requires complete, valid JSON.
        from pydantic_core import from_json

        if calls:
            arguments = calls[min(calls)]["function"]["arguments"]
            try:
                value = from_json(arguments, allow_partial="trailing-strings")
                code = value.get("code", "") if isinstance(value, dict) else ""
                return code if isinstance(code, str) else ""
            except ValueError:
                return ""
        blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)(?:```|$)", content, re.S)
        return blocks[-1] if blocks else (content if re.match(r"\s*(?:from |import |def )", content) else "")


    @weave.op(
        name="gridworld_agent_turn", kind="llm",
        postprocess_inputs=lambda values: {
            "model": values["model_name"], "messages": values["messages"],
            "tools": [RUN_PYTHON_TOOL], "seed": values["seed"], "thinking": values["thinking"],
            **inference_options(values["model_name"], values["thinking"], task="agent"),
        },
        postprocess_output=lambda result: result["completion"],
    )
    def agent_turn(model_name, messages, thinking, seed, on_code=None):
        from weave.trace.context.call_context import tracing_disabled

        content, reasoning, calls = "", "", {}
        finish_reason, usage = None, None
        completion_id, created, response_model = "", 0, model_name
        last_preview, last_update = "", 0.0
        argument_chunks, code_updates = 0, 0

        def emit_preview(force=False):
            nonlocal last_preview, last_update, code_updates
            now = time.monotonic()
            if not force and now - last_update < 0.15:
                return
            preview = preview_agent_code(content, calls)
            if preview and preview != last_preview:
                last_preview, last_update = preview, now
                code_updates += 1
                if on_code is not None:
                    on_code(preview)

        # Weave 0.52.38 drops arguments in the first tool-call chunk. Trace the complete
        # assembled response on this op instead of its broken automatic child span.
        # Exceptions still reach this op, and the response retains token usage.
        with tracing_disabled():
            with request_agent_stream(model_name, messages, thinking, seed) as stream:
                for chunk in stream:
                    completion_id = chunk.id or completion_id
                    created = chunk.created or created
                    response_model = chunk.model or response_model
                    if chunk.usage is not None:
                        usage = chunk.usage.model_dump(exclude_none=True)
                    if not chunk.choices:
                        continue
                    choice = chunk.choices[0]
                    delta = choice.delta
                    finish_reason = choice.finish_reason or finish_reason
                    if delta is None:
                        continue
                    content += delta.content or ""
                    reasoning += getattr(delta, "reasoning", None) or getattr(delta, "reasoning_content", None) or ""
                    for part in delta.tool_calls or []:
                        call = calls.setdefault(part.index, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                        if part.id:
                            call["id"] = part.id
                        if part.function:
                            call["function"]["name"] += part.function.name or ""
                            call["function"]["arguments"] += part.function.arguments or ""
                            argument_chunks += bool(part.function.arguments)
                    emit_preview()
        emit_preview(force=True)
        message = {"role": "assistant", "content": content or None}
        if calls:
            message["tool_calls"] = [calls[index] for index in sorted(calls)]
            for index, call in enumerate(message["tool_calls"]):
                call["id"] = call["id"] or f"call_{seed}_{index}"
        if reasoning:
            message["reasoning_content"] = reasoning
        completion = {
            "id": completion_id, "object": "chat.completion",
            "created": created, "model": response_model,
            "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
        }
        if usage is not None:
            completion["usage"] = usage
            current_call = weave.get_current_call()
            if current_call is not None:
                model_usage = {"requests": 1, **usage}
                cached = usage.get("prompt_tokens_details", {}).get("cached_tokens")
                if cached is not None:
                    model_usage["cache_read_input_tokens"] = cached
                current_call.summary = {**(current_call.summary or {}), "usage": {response_model: model_usage}}
        return {
            "message": message, "finish_reason": finish_reason, "completion": completion,
            "stream_stats": {"argument_chunks": argument_chunks, "code_updates": code_updates},
        }


    return AGENT_PROMPT, agent_turn


@app.cell(hide_code=True)
def agent_loop(API_KEY, agent_turn, run_in_sandbox):
    def verify_agent_plan(plan, puzzle):
        if not isinstance(plan, list) or not all(isinstance(action, str) for action in plan):
            raise ValueError("solve(world) must return a JSON list of action-name strings.")
        if len(plan) > 200:
            raise ValueError("The plan exceeds the 200-action limit.")
        world = bp.World(puzzle)
        invalid = sorted(set(plan) - set(world.action_space))
        if invalid:
            raise ValueError(f"Unknown or disallowed actions: {invalid}")
        return world.act(plan)


    def agent_progress(attempts, status="", code=None):
        parts = [mo.md("### 🤖 The model writes and runs code")]
        for attempt in attempts:
            icon = "✅" if attempt["status"] == "solved" else "↻"
            parts.append(mo.md(f"**Turn {attempt['turn']} · {icon}** " + html.escape(attempt["summary"])))
            warning = attempt.get("sandbox", {}).get("cleanup_warning")
            if warning:
                parts.append(mo.callout(mo.md(html.escape(warning.replace(API_KEY, "[redacted]"))), kind="warn"))
        if status:
            parts.append(mo.md("⏳ " + status))
        if code is None:
            code = attempts[-1].get("code", "") if attempts else ""
        if code:
            parts.append(mo.Html(
                '<pre style="white-space:pre-wrap;overflow:auto;max-height:360px;'
                'padding:14px;border:1px solid #8884;border-radius:8px;font-size:0.8rem">'
                '<code>' + html.escape(code) + '</code></pre>'
            ))
        return mo.vstack(parts)


    def run_code_agent(model_name, prompt, world, puzzle, thinking, seed, close_loop=True, on_update=None):
        started = time.monotonic()
        messages = [{"role": "user", "content": prompt}]
        attempts, last_plan = [], []
        last_verdict, sandbox_runs = None, 0
        max_turns = 6 if close_loop else 1
        status = "exhausted" if close_loop else "stopped"

        def update(text, code=""):
            if on_update is not None:
                on_update(attempts, text, code)

        for turn in range(max_turns):
            update(f"Turn {turn + 1} · Writing Python…")
            try:
                response = agent_turn(
                    model_name, messages, thinking, seed + turn,
                    on_code=lambda code: update(f"Turn {turn + 1} · Receiving Python…", code),
                )
            except Exception as error:
                attempts.append({"turn": turn + 1, "status": "error", "summary": "Inference failed: " + str(error).replace(API_KEY, "[redacted]")})
                status = "error"
                break
            message = response["message"]
            messages.append(message)
            calls = message.get("tool_calls", [])
            code, feedback = "", None
            if response["finish_reason"] == "length":
                feedback = {"error": "Your response was truncated at the token limit. Write a shorter complete solve(world) program and call run_python again."}
            elif len(calls) > 1:
                feedback = {"error": "Call run_python once per turn so you can use its feedback before your next attempt."}
            elif calls:
                try:
                    function = calls[0]["function"]
                    if function["name"] != "run_python":
                        raise ValueError("Use the run_python tool.")
                    arguments = json.loads(function["arguments"])
                    code = arguments.get("code")
                    if not isinstance(code, str) or not code.strip():
                        raise ValueError("The code argument must contain a complete Python program.")
                except (ValueError, TypeError, AttributeError) as error:
                    feedback = {"error": "Invalid tool call: " + str(error)}
            else:
                # Keep the original notebook's fallback for models that write a code block.
                text = message.get("content") or ""
                blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
                candidate = blocks[-1].strip() if blocks else text.strip()
                try:
                    tree = ast.parse(candidate)
                    if any(isinstance(node, ast.FunctionDef) and node.name == "solve" for node in tree.body):
                        code = candidate
                    else:
                        raise ValueError("Missing solve(world).")
                except (SyntaxError, ValueError):
                    feedback = {"error": "Use run_python with a complete solve(world) program. A hand-written action list has not been executed or verified."}

            attempt = {"turn": turn + 1, "status": "error", "code": code, "stream_stats": response.get("stream_stats", {})}
            if feedback is None:
                update(f"Turn {turn + 1} · Running Python in the Sandbox…", code)
                sandbox_result = run_in_sandbox(code, world)
                sandbox_runs += 1
                attempt["sandbox"] = sandbox_result
                feedback = {
                    "execution_status": sandbox_result["status"],
                    "stdout": sandbox_result.get("stdout", "")[-2000:],
                    "stderr": sandbox_result.get("stderr", "")[-2000:],
                }
                if sandbox_result["status"] != "completed":
                    feedback["error"] = sandbox_result["error"]
                    attempt["summary"] = "Python did not run successfully. " + sandbox_result["error"].replace(API_KEY, "[redacted]")
                else:
                    try:
                        plan = sandbox_result["plan"]
                        verdict = verify_agent_plan(plan, puzzle)
                        last_plan, last_verdict = plan, verdict
                        feedback.update(plan=plan, verifier=verdict)
                        attempt["verdict"] = verdict
                        attempt["status"] = "solved" if verdict["success"] else "unsolved"
                        attempt["summary"] = (
                            f"{'Solved' if verdict['success'] else 'Not solved'} · "
                            f"{verdict['gems_collected']}/{verdict['total_gems']} gems · "
                            f"goal reached: {verdict['reached_goal']} · "
                            f"{len(plan)} actions" + (" · stepped on lava" if verdict["died"] else "")
                        )
                    except Exception as error:
                        feedback["error"] = "Invalid plan: " + str(error)
                        attempt["summary"] = feedback["error"]
            else:
                attempt["summary"] = feedback["error"]
            attempts.append(attempt)
            solved = attempt["status"] == "solved"
            feedback["instruction"] = (
                "Wanderland verified this plan. The task is complete." if solved else
                "Read the execution and verifier feedback. Fix your code and call run_python again. Collect EVERY gem and finish on the goal without stepping on lava."
            )
            feedback_text = json.dumps(feedback).replace(API_KEY, "[redacted]")
            if calls:
                for call in calls:
                    messages.append({"role": "tool", "tool_call_id": call["id"], "name": call["function"]["name"], "content": feedback_text})
            else:
                messages.append({"role": "user", "content": feedback_text})
            update("", code)
            if solved:
                status = "solved"
                break
        return {
            "status": status, "plan": last_plan, "verdict": last_verdict,
            "attempts": attempts, "messages": messages, "sandbox_runs": sandbox_runs,
            "seconds": round(time.monotonic() - started, 2),
        }


    return agent_progress, run_code_agent


@app.cell(hide_code=True)
def agent_attempt(
    AGENT_PROMPT,
    API_KEY,
    WORLD,
    agent_button,
    agent_close_loop,
    agent_progress,
    agent_thinking,
    gen_plan,
    gen_puzzle,
    llm_seed,
    model_selector,
    run_code_agent,
    thinking_can_toggle,
    weave_url,
):
    mo.stop(not agent_button.value, mo.md("_Press **Plan with code** to write, run, and check a solution._"))
    mo.stop(not API_KEY, mo.md("_Connect to W&B first._"))
    agent_result = run_code_agent(
        model_selector.value, AGENT_PROMPT, WORLD, gen_puzzle,
        agent_thinking.value if thinking_can_toggle else None,
        int(llm_seed.value), close_loop=agent_close_loop.value,
        on_update=lambda attempts, status, code: mo.output.replace(agent_progress(attempts, status, code)),
    )
    _solved = agent_result["status"] == "solved"
    _summary = (
        f"**Mo solved it!** {len(agent_result['plan'])} actions (oracle: {len(gen_plan)})."
        if _solved else
        "**No verified solution yet.** " + (
            "The agent used all six turns." if agent_result["status"] == "exhausted" else
            "The run stopped after an inference error." if agent_result["status"] == "error" else
            "Close the loop is off, so the agent made one attempt."
        )
    )
    _parts = [
        agent_progress(agent_result["attempts"]),
        mo.callout(mo.md(_summary), kind="success" if _solved else "warn"),
        mo.md(f"**{agent_result['sandbox_runs']} Sandbox run{'s' if agent_result['sandbox_runs'] != 1 else ''} · {agent_result['seconds']:.1f}s** · [Open Weave traces]({weave_url})"),
    ]
    if agent_result["verdict"] is not None:
        agent_world = bp.World(gen_puzzle, speed=2.0)
        agent_world.act(agent_result["plan"])
        agent_scene = mo.ui.anywidget(agent_world)
        _parts.extend([
            mo.md("### Mo plays the agent's plan\nPress **Run My Code** in the scene to replay the returned actions."),
            agent_scene,
        ])
    mo.vstack(_parts)
    return


@app.cell(hide_code=True)
def evaluation_intro():
    mo.md("""
    ## Act 4 · Let the numbers settle it

    As the world grows, does each approach hold up? Compare the original four
    approaches: **plan without thinking**, **plan with thinking**, **write code**,
    and **code + verifier feedback**.

    These are the **recorded results from the original Can LLMs Plan experiment**,
    now stored in W&B Tables. They used local Gemma inference; the timings below
    do not measure today's W&B Inference or CoreWeave Sandboxes.
    """)
    return


@app.cell(hide_code=True)
def evaluation_source():
    import wandb
    import pandas as pd
    import altair as alt

    # Pinned artifact version: the source data cannot silently change mid-demo.
    EVALUATION_ARTIFACT = "wandb/servless-sandbox-tutorial/can-llms-plan-original-results:v0"
    EVALUATION_RUN_URL = "https://wandb.ai/wandb/servless-sandbox-tutorial/runs/planning-import-be5cf953b11f"
    EVALUATION_METHODS = {
        "plan_nothink": "plan · no-think", "plan_think": "plan · think",
        "code": "write code", "code_fb": "code + verifier",
    }
    EVALUATION_COLORS = ["#d4564a", "#e0912f", "#2a9d4a", "#14532d"]

    def load_evaluation(api_key, artifact_ref):
        artifact = wandb.Api(api_key=api_key, timeout=30).artifact(artifact_ref)
        table = artifact.get("planning_results")
        return pd.DataFrame(table.data, columns=table.columns)

    def evaluation_world(record):
        # Replay the recorded map, not a regenerated map whose implementation may change.
        world = json.loads(record["world_json"])

        def object_from_dict(value):
            contents = value.get("contains")
            return bp.Obj(
                value["type"], color=value.get("color"), state=value.get("state"),
                contains=object_from_dict(contents) if isinstance(contents, dict) else None,
                blocking=value.get("blocking", True),
            )

        objects = {tuple(obj["pos"]): object_from_dict(obj) for obj in world["objects"]}
        kinds = {obj.type for obj in objects.values()}
        actions = ["move_forward", "turn_left", "turn_right"]
        if "gem" in kinds:
            actions.append("collect_gem")
        if "key" in kinds:
            actions.append("pickup")
        if "door" in kinds:
            actions.append("toggle")
        return bp.Puzzle(
            name="Recorded Wildlands", cols=world["cols"], rows=world["rows"],
            start=tuple(world["start"]), goal=tuple(world["goal"]),
            heading="NESW"[world["heading"]] if isinstance(world["heading"], int) else world["heading"],
            actions=tuple(actions), objects=objects,
            walls=[tuple(p) for p in world["walls"]],
            gaps=[tuple(p) for p in world["water"]],
            lava=[tuple(p) for p in world["lava"]],
        )
    return alt, EVALUATION_ARTIFACT, EVALUATION_RUN_URL, EVALUATION_METHODS, EVALUATION_COLORS, load_evaluation, evaluation_world


@app.cell(hide_code=True)
def evaluation_load(API_KEY, EVALUATION_ARTIFACT, EVALUATION_RUN_URL, load_evaluation):
    mo.stop(not API_KEY, mo.md("_Connect W&B above to load the recorded results._"))
    try:
        evaluation_df = load_evaluation(API_KEY, EVALUATION_ARTIFACT)
    except Exception as _error:
        mo.stop(True, mo.callout(mo.md(
            "Could not load the W&B results Table. Check your connection and access, then rerun this cell.\n\n"
            + html.escape(str(_error).replace(API_KEY, "[redacted]"))
        ), kind="warn"))
    mo.stop(evaluation_df.empty, mo.md("_This results Table is empty._"))
    _errors = int(evaluation_df.harness_error.fillna("").str.strip().ne("").sum())
    _models = ", ".join(evaluation_df.model_id.unique())
    mo.md(
        f"📊 **{len(evaluation_df)} recorded runs** · {_errors} harness errors · `{_models}` · "
        f"{evaluation_df.method_label.nunique()} approaches · grids "
        f"{int(evaluation_df.cols.min())}×{int(evaluation_df.rows.min())} to "
        f"{int(evaluation_df.cols.max())}×{int(evaluation_df.rows.max())}.\n\n"
        f"[Open results in W&B Tables]({EVALUATION_RUN_URL}) · "
        "[Tables documentation](https://docs.wandb.ai/models/tables)\n\n"
        "Three world seeds were used; some grid/approach combinations have fewer records. "
        "Hover over a chart point for its sample count."
    )
    return (evaluation_df,)


@app.cell(hide_code=True)
def evaluation_chart(evaluation_df, EVALUATION_METHODS, EVALUATION_COLORS, alt):
    _aggregate = evaluation_df.groupby(["method_label", "cols", "rows"]).agg(
        success=("solved", "mean"), wall=("wall_time_s", "median"),
        tokens=("output_tokens", "median"), n=("solved", "size"),
    ).reset_index()
    _aggregate["approach"] = _aggregate.method_label.map(EVALUATION_METHODS)
    _domain = list(EVALUATION_METHODS.values())
    _base = alt.Chart(_aggregate).encode(
        x=alt.X("cols:Q", title="grid size (n × n)", scale=alt.Scale(nice=False)),
        color=alt.Color("approach:N", scale=alt.Scale(domain=_domain, range=EVALUATION_COLORS), legend=None),
        tooltip=[
            alt.Tooltip("approach:N", title="approach"), alt.Tooltip("cols:Q", title="grid size"),
            alt.Tooltip("success:Q", title="solved", format=".0%"),
            alt.Tooltip("wall:Q", title="median seconds", format=".1f"),
            alt.Tooltip("tokens:Q", title="median tokens", format=",.0f"),
            alt.Tooltip("n:Q", title="recorded runs"),
        ],
    ).mark_line(point=alt.OverlayMarkDef(size=65, filled=True), strokeWidth=3)
    _success = _base.encode(y=alt.Y("success:Q", title="fraction solved", scale=alt.Scale(domain=[0, 1]))).properties(
        title="Success (higher is better)", width=290, height=245)
    _cost = _base.encode(y=alt.Y("wall:Q", title="median wall-time (s)")).properties(
        title="Cost (lower is better)", width=290, height=245)
    _legend = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;margin:0 10px">'
        f'<span style="width:11px;height:11px;border-radius:50%;background:{color};display:inline-block"></span>{label}</span>'
        for label, color in zip(_domain, EVALUATION_COLORS)
    )
    mo.vstack([
        mo.md("**Success and compute cost vs. grid size, by planning strategy**"),
        mo.Html(f'<div style="display:flex;justify-content:center;flex-wrap:wrap;font-size:13px">{_legend}</div>'),
        mo.center(mo.ui.altair_chart(alt.hconcat(_success, _cost), chart_selection=False, legend_selection=False)),
    ])
    return


@app.cell(hide_code=True)
def evaluation_summary(evaluation_df, EVALUATION_METHODS):
    _code_tokens = evaluation_df[evaluation_df.method_label == "code"].output_tokens.median()
    _rows = []
    for _method, _label in EVALUATION_METHODS.items():
        _group = evaluation_df[evaluation_df.method_label == _method]
        if _group.empty:
            continue
        _tokens = _group.output_tokens.median()
        _ratio = f"{_tokens / _code_tokens:.1f}×" if _code_tokens > 0 else "—"
        _rows.append(
            f"| **{_label}** | {len(_group)} | {_group.solved.mean():.0%} | "
            f"{_group.wall_time_s.median():.1f} s | {_tokens:,.0f} | {_ratio} |"
        )
    mo.md(
        "**What each approach costs.** Accuracy alongside the computation it took.\n\n"
        "| Approach | Runs | Solved | Median time | Median tokens | Tokens vs. code |\n"
        "|---|--:|--:|--:|--:|--:|\n" + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def evaluation_pick(evaluation_df, EVALUATION_METHODS):
    _records = evaluation_df.sort_values(["cols", "method_label", "world_seed"]).to_dict("records")
    _options = {
        f"{EVALUATION_METHODS[row['method_label']]} · {row['cols']}×{row['rows']} · "
        f"seed {row['world_seed']} · {'solved' if row['solved'] else 'failed'}": row["run_id"]
        for row in _records
    }
    evaluation_pick = mo.ui.dropdown(options=_options, value=None, label="Inspect a recorded run", full_width=True)
    mo.accordion({"🔍 Replay a recorded result in Mo's world": evaluation_pick})
    return (evaluation_pick,)


@app.cell(hide_code=True)
def evaluation_replay(evaluation_df, evaluation_pick, evaluation_world, EVALUATION_METHODS):
    if evaluation_pick.value is None:
        _view = mo.md("Choose a recorded run above to replay its plan, including failed attempts.")
    else:
        _record = evaluation_df[evaluation_df.run_id == evaluation_pick.value].iloc[0].to_dict()
        _world = bp.World(evaluation_world(_record))
        _plan = _record["plan"]
        _verdict = _world.act(_plan)
        _widget = mo.ui.anywidget(_world)
        _status = "✅ solved" if _record["solved"] else "❌ failed"
        _views = [
            mo.md(f"### {EVALUATION_METHODS[_record['method_label']]} · {_record['cols']}×{_record['rows']} · {_status}"),
            mo.md(f"World seed **{_record['world_seed']}** · {len(_plan)} actions · "
                  f"{_record['wall_time_s']:.1f} s · {_record['output_tokens']:,} output tokens. "
                  + ("Press **Run** in the scene to watch the recorded plan." if _plan else "No actions were recorded; inspect the model output below.")),
            _widget,
            mo.accordion({"Recorded plan and model output": mo.vstack([
                mo.md("```json\n" + json.dumps(_plan, indent=2) + "\n```"),
                mo.Html('<pre style="white-space:pre-wrap;max-height:320px;overflow:auto">'
                        + html.escape(_record.get("raw_output") or "No output was recorded.") + '</pre>'),
            ])}),
        ]
        if bool(_verdict["success"]) != bool(_record["solved"]):
            _views.insert(1, mo.callout(mo.md("Today's replay verdict differs from the recorded result; the charts retain the original score."), kind="warn"))
        _view = mo.vstack(_views)
    _view
    return


@app.cell(hide_code=True)
def evaluation_takeaway(evaluation_df):
    _code = evaluation_df[evaluation_df.method_label == "code"]
    _loop = evaluation_df[evaluation_df.method_label == "code_fb"]
    _direct = evaluation_df[evaluation_df.method_label == "plan_nothink"]
    _thinking = evaluation_df[evaluation_df.method_label == "plan_think"]
    mo.md(f"""
    ### The verdict from this experiment

    - Direct planning solved **{int(_direct.solved.sum())}/{len(_direct)}** recorded worlds without
      thinking and **{int(_thinking.solved.sum())}/{len(_thinking)}** with thinking.
    - Writing a planner solved **{int(_code.solved.sum())}/{len(_code)}**;
      adding verifier feedback solved **{int(_loop.solved.sum())}/{len(_loop)}**.
    - Compare the success curve with the time and token cost. A stronger harness
      can change the outcome without changing the model's weights.

    These results describe this recorded Gemma experiment, not every model or
    harness. Our W&B demo uses a different inference service and execution setup;
    measuring it on the same worlds is the next experiment.
    """)
    return



if __name__ == "__main__":
    app.run()
