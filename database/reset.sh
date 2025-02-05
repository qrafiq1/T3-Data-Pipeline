echo  "Restting redshift database schema..."
psql -h c14-rs-cluster.cdq12ms5gjyk.eu-west-2.redshift.amazonaws.com -p 5439 -U qasim_rafiq -d trucks -f schema.sql
echo "Has been reset!"