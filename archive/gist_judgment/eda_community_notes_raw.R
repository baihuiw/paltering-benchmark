# ============================================================================
# eda_community_notes_raw.R
# Part-by-part EDA of the RAW Community Notes "Notes data" TSV shards
# (downloaded from https://x.com/i/communitynotes/download-data).
#
# Files expected in ~/Downloads:  notes-00000.tsv, notes-00001.tsv, notes-00002.tsv
#   - the three shards are DISJOINT (no shared noteIds); together = full corpus
#     2021-01 -> 2026-07, ~2.88M notes on ~1.93M posts.
#
# Run section by section (Cmd+Enter in RStudio). Section 1 must run first;
# everything after is independent.
# ============================================================================

## ---- 0. setup --------------------------------------------------------------
library(data.table)   # fast TSV reader
library(bit64)        # 64-bit ints, needed to decode tweetId timestamps

DL    <- path.expand("~/Downloads")
QUICK <- FALSE   # TRUE = load only the 2 small shards (~29k rows, instant)
                 # FALSE = also load the 1.3 GB bulk shard (~30-60 s)

## ---- 1. load the shards -----------------------------------------------------
files <- file.path(DL, c("notes-00000.tsv", "notes-00001.tsv", "notes-00002.tsv"))
if (QUICK) files <- files[1:2]

# quote = "" is important: fields are never quoted in these TSVs
notes <- rbindlist(lapply(files, fread, sep = "\t", quote = "",
                          colClasses = list(character = c("noteId", "tweetId"))))
notes <- notes[classification != ""]                     # a couple of blank rows
notes[, note_time := as.POSIXct(createdAtMillis / 1000,
                                origin = "1970-01-01", tz = "UTC")]
dim(notes)          # rows x cols
range(notes$note_time)

## ---- 2. structure: what is one row? ----------------------------------------
# One row = ONE NOTE written by one contributor about one post (tweetId).
# A post can have many notes; a note has exactly one post.
str(notes, max.level = 1)

# The full column list, grouped by meaning:
#   noteId, noteAuthorParticipantId  ...ids (author id is hashed)
#   createdAtMillis                  ...when the NOTE was written
#   tweetId                          ...the POST the note is about (numeric id
#                                       only -- the post text is NOT included)
#   classification                   ...note's verdict: MISINFORMED_OR_
#                                       POTENTIALLY_MISLEADING vs NOT_MISLEADING
#   believable/harmful/validationDifficulty ...legacy fields, mostly empty now
#   misleading*  (7 flags)           ...WHY the post misleads (tick-all-that-apply)
#   notMisleading* (4 flags)         ...why the post is fine
#   trustworthySources               ...note cites sources? (1/0)
#   summary                          ...THE NOTE'S TEXT (the only free text here)
#   isMediaNote, isCollaborativeNote ...note about media? written collaboratively?

## ---- 3. variable-by-variable tour -------------------------------------------
notes[, .N, by = classification]                          # verdict split
notes[, .N, by = trustworthySources]
notes[, .N, by = isMediaNote]
notes[, .N, by = isCollaborativeNote]
notes[, .(n_notes = .N, n_posts = uniqueN(tweetId),
          n_authors = uniqueN(noteAuthorParticipantId))]

# legacy fields -- confirm they're mostly empty (they were retired early on):
notes[, .N, by = believable][order(-N)]
notes[, .N, by = harmful][order(-N)]

## ---- 4. misleading-type taxonomy (maps onto the gist/verbatim 2x2) ----------
mis <- notes[classification == "MISINFORMED_OR_POTENTIALLY_MISLEADING"]
flag_cols <- grep("^misleading", names(mis), value = TRUE)
mis_taxonomy <- mis[, lapply(.SD, function(x) mean(x == 1, na.rm = TRUE)),
                    .SDcols = flag_cols]
round(sort(unlist(mis_taxonomy), decreasing = TRUE), 3)
# reading guide:  missingImportantContext ~ PALTER (true-but-misleading)
#                 outdatedInformation     ~ temporal laundering
#                 factualError / unverifiedClaimAsFact ~ verbatim-false claims

## ---- 5. notes per post -------------------------------------------------------
per_post <- notes[, .N, by = tweetId]
table(cut(per_post$N, c(0, 1, 2, 4, 10, Inf),
          labels = c("1", "2", "3-4", "5-10", "11+")))
per_post[order(-N)][1:5]                                  # most-noted posts

## ---- 6. the note text ---------------------------------------------------------
notes[, sum_len := nchar(summary)]
summary(notes$sum_len)
mean(grepl("http", notes$summary, fixed = TRUE))          # share citing a URL

# read a few actual notes (palter-adjacent category):
mis[misleadingMissingImportantContext == 1 & nchar(summary) %between% c(120, 300),
    .(tweetId, summary)][1:5]

## ---- 7. timeline: what CAN be dated ------------------------------------------
# The post itself is not in the data, but its creation time is recoverable:
# tweetId is a Twitter "snowflake": creation_ms = (id >> 22) + 1288834974657
ok <- notes[nchar(tweetId) >= 15]
post_ms <- as.integer64(ok$tweetId) %/% as.integer64(4194304) +
           as.integer64(1288834974657)
ok[, post_time := as.POSIXct(as.numeric(post_ms) / 1000,
                             origin = "1970-01-01", tz = "UTC")]
ok[, delay_h := as.numeric(difftime(note_time, post_time, units = "hours"))]
summary(ok$delay_h)          # post -> note lag; median ~9.6h
# NOTE: that is ALL the timeline there is. No reposts, no cascades, no
# engagement -- this file describes notes, not how the post spread.

## ---- 8. quick plots -----------------------------------------------------------
op <- par(mfrow = c(1, 2), mar = c(4.5, 4.5, 2.5, 1))
mon <- notes[, .N, by = .(m = as.Date(cut(note_time, "month")))][order(m)]
plot(mon$m, mon$N, type = "l", lwd = 2, xlab = "month", ylab = "notes written",
     main = "Community Notes volume")
hist(pmin(ok$delay_h, 168), breaks = 60, xlab = "hours from post to note (capped 7d)",
     main = "How fast notes arrive", col = "grey80", border = NA)
par(op)
