# Gampy

Tool for calculation of the precise point position (PPP) error using GAMP utility.

## Configuration file

```
{
  "obsDir": "/path/to/obs/dir",
  "navDir": "/path/to/nav/dir",
  "sp3Dir": "/path/to/sp3/dir",
  "clkDir": "/path/to/clk/dir",
  "outDir": "/path/to/out/dir",
  // "gps" | "glo" | "gps+glo" | "gal" | "qzs" | "bsd"
  "navSys": "gps",
  // "spp" | "ppp_kinematic" | "ppp_static"
  "posMode": "ppp_kinematic",
  // "INFO" | "WARNING" | "ERROR"
  "logLevel": "WARNING"
}
```
