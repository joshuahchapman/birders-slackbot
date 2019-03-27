# Birders Slackbot

This project powers the interactive "slash commands" available in the [Birders Slack workspace](https://github.com/birders-slack/documentation/blob/master/README.md).

## Overview

The following slash commands are available:

`/ebird`: Pull data from eBird.org.

`/5mr`: Manage your personal saved locations.

## Usage Details

### ebird

The following subcommands are available for `/ebird`:

`recent`

`recent_notable`

### 5mr

The following subcommands are available for `/5mr`:

**add_circle**: Creates a new circle.

| Parameter | Required? | Notes | Default Value | Example |
| --------- | --------- | ----- | ------------- | ------- |
| latitude  | YES       |       |               | 38.940365 |
| longitude | YES       |       |               | -74.9212611 |
| radius_km | no        | Radius of the circle in km | 8 | 3 |
| name      | no        | A name for the circle | circle1 | HomeCircle |


**list_circles**: Lists your circles. No parameters.

**set_default**

**recent**

**recent_notable**
