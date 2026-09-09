# ============================================================================
# eda_slaughter_pnas.R
# Part-by-part EDA of the Slaughter et al. (PNAS 2025) replication data:
#   "Community notes reduce engagement with and diffusion of false information"
#   Harvard Dataverse doi:10.7910/DVN/K0RQTM  (CC BY-NC-SA 4.0)
#
# Files expected in ~/Downloads: data.tar.gz.part-1 / -2 / -3  (~5.4 GB total)
#
# Vocabulary used by the authors:
#   "slap"  = the moment a note is attached to the post
#   CRH     = note status "Currently Rated Helpful" (the note shows publicly)
#   de-identified clock: all timestamps are SHIFTED so the post's publication
#     is 1970-01-01 00:00 -- only RELATIVE time is meaningful.
#   tweet_id / author_id / note_id are HASHED (cannot be joined back to X).
#
# Run section by section. Section 1 is a ONE-TIME extraction.
# ============================================================================

## ---- 0. setup ---------------------------------------------------------------
library(data.table)
library(nanoparquet)   # light parquet reader (no arrow needed)

DL <- path.expand("~/Downloads")
# after full extraction the data lives here:
FULL_DIR   <- file.path(DL, "slaughter_pnas_data", "data")
# a small pre-extracted sample (metadata + 2 example posts) lives here:
SAMPLE_DIR <- file.path(DL, "slaughter_pnas_sample", "data")
ROOT <- if (dir.exists(FULL_DIR)) FULL_DIR else SAMPLE_DIR
cat("reading from:", ROOT, "\n")

## ---- 1. (ONE-TIME) combine the 3 parts and extract everything ----------------
# Needs ~12 GB free disk and a few minutes. Flip FALSE -> TRUE and run once,
# or paste the two shell commands in Terminal yourself.
if (FALSE) {
  dir.create(file.path(DL, "slaughter_pnas_data"), showWarnings = FALSE)
  system(paste0("cat ", DL, "/data.tar.gz.part-* | tar -xzf - -C ",
                DL, "/slaughter_pnas_data"))
}

## ---- 2. tweet_metadata: one row per analyzed post -----------------------------
tw <- as.data.table(read_parquet(file.path(ROOT, "tweet_metadata.parquet")))
dim(tw)                                   # 39,586 posts x 99 cols
names(tw)

# Column groups (99 cols, but only 5 groups):
#  * ids:            tweet_id, author_id           <- HASHED, not real X ids
#  * author:         author_n_followers
#  * text:           PCA_20_embd_0..19, PCA_58_embd_0..57
#                    <- the tweet TEXT itself is NOT included; only PCA-reduced
#                       embeddings of it (used as matching covariates)
#  * CN taxonomy:    tweet_rated_misleading_* (share of the post's notes
#                    ticking each misleading-type flag)
#  * covariate bins: partisan_lean, hours_to_slap_bin,
#                    pre_break_calculated_retweets_bin, *_flesch_kincaid_*,
#                    note_text_sentence_count(_bin), total_number_of_ratings,
#                    created_at, tweet_media, tweet_language

# per-variable tour of the non-embedding columns:
tw[, .N, by = tweet_language][order(-N)][1:8]
tw[, .N, by = tweet_media][order(-N)]
tw[, .N, by = partisan_lean]
tw[, .N, by = hours_to_slap_bin]
summary(tw$author_n_followers)
tax_cols <- grep("^tweet_rated_misleading", names(tw), value = TRUE)
round(colMeans(tw[, ..tax_cols], na.rm = TRUE), 3)   # taxonomy rates, per post

## ---- 3. note_metadata: which notes ever went public ---------------------------
nt <- as.data.table(read_parquet(file.path(ROOT, "note_metadata.parquet")))
dim(nt)                                   # 73,061 notes x 3 cols
head(nt)
nt[, .N, by = ever_crh_in_48h_post_slap]  # note reached "Currently Rated Helpful"?
nt[, .(notes_per_post = .N), by = tweet_id][, table(pmin(notes_per_post, 5))]

## ---- 4. b_merged: ONE post's engagement series (15-min resolution) ------------
bdir <- file.path(ROOT, "cn_effect_intermediate_prod", "b_merged")
bfiles <- list.files(bdir, pattern = "\\.parquet$", full.names = TRUE)
length(bfiles)        # one file per post (~40k when fully extracted)

b <- as.data.table(read_parquet(bfiles[1]))
dim(b)                # ~2,000 rows x 37 cols = one row per 15-min tick
names(b)

# What each row of a post's series holds:
#  * timestamp / created_at / time_since_publication  (de-identified clock!)
#  * raw engagement counters:   impressions, retweets, likes, replies
#  * reconstructed counters:    calculated_retweets, calculated_replies
#  * CASCADE STRUCTURE:         rt_cascade_width, rt_cascade_depth,
#                               rt_cascade_wiener_index   <- structural
#                               virality of the repost cascade, over time
#  * note events for up to 3 notes: note_k_note_created_at,
#                               note_k_first_crh_time (when it went public),
#                               note_k_twitter_status
#  * bookkeeping: present_in_* flags, time_freq ("0.25h"), dev,
#                 volatile_tweet_filtering

b[, hours := as.numeric(time_since_publication, units = "hours")]
summary(b$hours)                                  # how long the post is tracked
b[!is.na(likes), .(hours, impressions, retweets, likes,
                   calculated_retweets, rt_cascade_width, rt_cascade_depth)][1:10]

# when did the first note go public, in hours after publication?
crh_h <- as.numeric(difftime(b$note_0_first_crh_time[1], b$created_at[1],
                             units = "hours"))
crh_h

## ---- 5. plot one post: spread + the moment the note arrives -------------------
op <- par(mfrow = c(1, 2), mar = c(4.5, 4.5, 2.5, 1))
plot(b$hours, b$calculated_retweets, type = "s", lwd = 2,
     xlab = "hours since publication", ylab = "cumulative reposts",
     main = "one post's diffusion")
abline(v = crh_h, col = "red", lwd = 2, lty = 2)
text(crh_h, max(b$calculated_retweets, na.rm = TRUE) * .9,
     " note goes public", col = "red", adj = 0)
plot(b$hours, b$rt_cascade_wiener_index, type = "l", lwd = 2,
     xlab = "hours since publication", ylab = "Wiener index",
     main = "structural virality over time")
abline(v = crh_h, col = "red", lwd = 2, lty = 2)
par(op)

## ---- 6. treatment effects: the paper's headline objects ------------------------
# 1.3M rows = posts x event-time; t_* treated, c_* synthetic control, te_* effect.
# 194 MB file -- read only the columns you need:
te <- as.data.table(read_parquet(
  file.path(ROOT, "cn_effect_output", "treatment_effects", "main",
            "final_treatment_effects.parquet"),
  col_select = c("tweet_id", "note_0_hours_since_first_crh",
                 "t_calculated_retweets", "c_calculated_retweets",
                 "te_calculated_retweets", "te_rt_cascade_wiener_index")))
dim(te)

# average effect on reposts by hours since the note went public:
eff <- te[!is.na(te_calculated_retweets),
          .(mean_te = mean(te_calculated_retweets),
            mean_treated = mean(t_calculated_retweets, na.rm = TRUE),
            mean_control = mean(c_calculated_retweets, na.rm = TRUE), .N),
          by = .(h = round(note_0_hours_since_first_crh))][order(h)]
eff[h %in% c(0, 6, 12, 24, 48)]
# relative effect on CUMULATIVE reposts at 48h (~ -12%). The paper's headline
# "-45.7% reposts" is on POST-NOTE increments, not cumulative totals -- a
# cumulative -12% gap and an incremental -46% are consistent.
eff[h == 48, mean_te / mean_control]

## ---- 7. what this dataset does NOT contain -------------------------------------
# * post text (only PCA embeddings)  * note text (only length/readability bins)
# * real ids or absolute dates (hashed + de-identified relative clock)
# * individual reposters, follower graph, or quote-tweet text
#   -> it gives the human SPREAD CURVE + note-damping baseline;
#      text MUTATION along chains still needs e.g. Bluesky reply/quote trees.
