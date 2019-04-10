# Birders Slackbot

This project powers the interactive "slash commands" available in the [Birders Slack workspace](http://www.birders.info).

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

**add_circle**: Create a new circle.

Example commands:

```
/5mr add_circle 38.940365 -74.9212611
/5mr add_circle 38.940365 -74.9212611 radius_km=15 name=HomeCircle
```

| Parameter | Required? | Notes | Default Value | Example |
| --------- | --------- | ----- | ------------- | ------- |
| latitude  | YES       |       |               | 38.940365 |
| longitude | YES       |       |               | -74.9212611 |
| radius_km | no        | Radius of the circle in km | 8 | 15 |
| name      | no        | A name for the circle | circle1 | home5mr |

**list_circles**: List your circles. No parameters.

**set_default**: Set one of your circles to be the default, which will be used in queries where you don't specify a circle.

Example command:

```
/5mr set_default circle1
```
| Parameter | Required? | Notes | Default Value | Example |
| --------- | --------- | ----- | ------------- | ------- |
| name      | YES       | The name of one of your existing circles | | circle1 |

**recent**: Pull recent observations from eBird. This command accepts all the optional parameters of eBird's "Recent nearby observations" request, which you can read about [here](https://documenter.getpostman.com/view/664302/ebird-api-20/2HTbHW#b785f3da-1802-d4e0-c447-85cb54abd0bb).

Example commands:

```
/5mr recent
/5mr recent circle_name=circle2
/5mr recent back=3
/5mr recent maxResults=20
```

| Parameter | Required? | Notes | Default Value | Example |
| --------- | --------- | ----- | ------------- | ------- |
| circle_name | no | The name of one of your existing circles | The circle you have flagged as your default | circle2 |

**recent_notable**: Pull recent "notable" observations (as defined by eBird) from eBird. This command accepts all the optional parameters of eBird's "Recent nearby notable observations" request, which you can read about [here](https://documenter.getpostman.com/view/664302/ebird-api-20/2HTbHW#cedc0e26-172f-598c-aa4d-9e552340b5e7).

Example commands:

```
/5mr recent_notable
/5mr recent_notable circle_name=circle2
/5mr recent_notable back=3
/5mr recent_notable maxResults=20
```

| Parameter | Required? | Notes | Default Value | Example |
| --------- | --------- | ----- | ------------- | ------- |
| circle_name | no | The name of one of your existing circles | The circle you have flagged as your default | circle2 |
