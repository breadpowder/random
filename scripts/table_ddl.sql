create table "Tickers"
(
	ticker SERIAL PRIMARY KEY,
	name varchar
);


create table "Tickers_Data_Daily"
(
  ticker   integer          not null
    constraint tickers_data_ticker_foreign
    references "Tickers",
  time     date             not null,
  low      double precision not null,
  high     double precision not null,
  open     double precision not null,
  close    double precision not null,
  volume   double precision,
  constraint "Tickers_Data_Daily_pkey"
  primary key (ticker, time)
);