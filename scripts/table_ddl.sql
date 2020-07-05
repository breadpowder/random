create table "Tickers"
(
	id SERIAL PRIMARY KEY,
	name varchar
);


create table "Tickers_Data"
(
  id  integer          not null
    constraint tickers_data_ticker_foreign
    references "Tickers",
  time     timestamp            not null,
  low      double precision not null,
  high     double precision not null,
  open     double precision not null,
  close    double precision not null,
  volume   double precision default -1.0,
  constraint "Tickers_Data_pkey"
  primary key (id, time)
);