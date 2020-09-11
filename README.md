# psql_service

This is a small console tool to browse the [PostgreSQL
services
file](https://www.postgresql.org/docs/current/libpq-pgservice.html)
and connect to them with psql. Designed to be a quick-fix for the
problem of there being "too many" servers to choose from.

## Dynamic DNS lookup

By default, psql is just launched with a direct reference to the
service, and will connect based on that. However, if the `hostaddr`
field is specified and starts with `!`, a directed DNS lookup will be
done. That is, the hostname specified in `host` will be looked up
using the DNS server specified in `hostaddr` (minus the `!` of
course).

This is particularly intended for environments where you cannot get
the IP address of the server directly, and have to perform a DNS
lookup which cannot be done using your primary DNS server. One common
example of this is accessing a RDS PostgreSQL instance on AWS through
a VPC.

# Hack warning

This is just a very quick hack. Use at your own risk :)
