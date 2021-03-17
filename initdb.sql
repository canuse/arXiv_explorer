create table stem_pair(
key text primary key,
value text
);
create table arxiv_rank(
word text,
paper text,
algorithm text,
rank_value float, id int default(0)
);
create table term_appearance(
    word text,
    document_freq int,
    term_freq text,
    id int default(0)
);
create table arxiv_document
(
	id SERIAL  primary key,
	arxiv_id text,
	submitter text,
	authors text,
	title text,
	comments text,
	doi text,
	report_no text,
	categories text,
	journal_ref text,
	license text,
	abstract text,
	versions text,
	update_date text,
	authors_parsed text
);