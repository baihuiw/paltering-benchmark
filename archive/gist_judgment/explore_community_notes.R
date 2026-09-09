# ============================================================================
# explore_community_notes.R
# Profile the raw X/Twitter Community Notes "Notes data" TSV shards and answer
# three fit-for-study questions for the Stage-4 agent-diffusion simulation:
#   Q1  Does the data contain the exact TEXT of the noted post?
#   Q2  Does it contain REPOSTS / diffusion cascades of the post?
#   Q3  Can a TIMELINE for the post be tracked?
#
# Data: https://x.com/i/communitynotes/download-data  (notes-0000*.tsv)
# Usage: Rscript explore_community_notes.R  [downloads_dir]
#        (defaults to ~/Downloads; writes figures to results/community_notes/)
# ============================================================================

suppressPackageStartupMessages({
  if (!requireNamespace("data.table", quietly = TRUE))
    install.packages("data.table", repos = "https://cloud.r-project.org")
  if (!requireNamespace("bit64", quietly = TRUE))
    install.packages("bit64", repos = "https://cloud.r-project.org")
  library(data.table); library(bit64)
})

args     <- commandArgs(trailingOnly = TRUE)
dl_dir   <- if (length(args) >= 1) args[1] else path.expand("~/Downloads")
out_dir  <- "results/community_notes"; dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

files <- sort(list.files(dl_dir, pattern = "^notes-\\d+\\.tsv$", full.names = TRUE))
stopifnot("No notes-*.tsv files found in the downloads dir" = length(files) > 0)

cat("============================================================\n")
cat("COMMUNITY NOTES — RAW NOTES DATA PROFILE\n")
cat("============================================================\n\n")

# ---- 1. load shards (quote='' : fields are never quoted in these TSVs) ------
keep <- c("noteId", "tweetId", "createdAtMillis", "classification",
          "misleadingFactualError", "misleadingManipulatedMedia",
          "misleadingOutdatedInformation", "misleadingMissingImportantContext",
          "misleadingUnverifiedClaimAsFact", "misleadingSatire", "misleadingOther",
          "trustworthySources", "summary")

shards <- lapply(files, function(f) {
  dt <- fread(f, sep = "\t", quote = "", select = keep,
              colClasses = list(character = c("noteId", "tweetId", "summary")))
  dt[, src := basename(f)]
  dt
})
notes <- rbindlist(shards)
notes <- notes[classification != ""]                       # drop rare blank rows
notes[, note_time := as.POSIXct(createdAtMillis / 1000,
                                origin = "1970-01-01", tz = "UTC")]

cat("---- Shards ----\n")
per_file <- notes[, .(rows = .N,
                      from = format(min(note_time), "%Y-%m-%d"),
                      to   = format(max(note_time), "%Y-%m-%d")), by = src]
print(per_file, row.names = FALSE)
cat(sprintf("\nTOTAL notes: %s   unique posts (tweetIds): %s   note-ID overlap across shards: %s\n",
            format(nrow(notes), big.mark = ","),
            format(uniqueN(notes$tweetId), big.mark = ","),
            nrow(notes) - uniqueN(notes$noteId)))

# ---- 2. what a row IS ------------------------------------------------------
cat("\n---- Columns present (full raw schema of the notes file) ----\n")
hdr <- names(fread(files[1], sep = "\t", quote = "", nrows = 0))
cat(paste(strwrap(paste(hdr, collapse = ", "), width = 78), collapse = "\n"), "\n")

# ---- 3. classification + misleading-taxonomy distribution ------------------
cat("\n---- Note verdict on the post ----\n")
print(notes[, .N, by = classification][order(-N)], row.names = FALSE)

cat("\n---- Misleading-type flags (among MISLEADING notes; note can tick several) ----\n")
mis <- notes[classification == "MISINFORMED_OR_POTENTIALLY_MISLEADING"]
flags <- c(missingImportantContext = "misleadingMissingImportantContext",
           factualError            = "misleadingFactualError",
           unverifiedClaimAsFact   = "misleadingUnverifiedClaimAsFact",
           manipulatedMedia        = "misleadingManipulatedMedia",
           outdatedInformation     = "misleadingOutdatedInformation",
           satire                  = "misleadingSatire",
           other                   = "misleadingOther")
flag_tab <- data.table(flag = names(flags),
                       n    = sapply(flags, function(cl) mis[, sum(get(cl) == 1, na.rm = TRUE)]))
flag_tab[, pct_of_misleading := sprintf("%.1f%%", 100 * n / nrow(mis))]
print(flag_tab[order(-n)], row.names = FALSE)
cat("  (missingImportantContext ~ PALTER analogue; outdatedInformation ~ temporal\n",
    "  laundering; factualError/unverified ~ verbatim-false claims)\n")

# ---- 4. notes per post -----------------------------------------------------
cat("\n---- Notes per post ----\n")
per_tweet <- notes[, .N, by = tweetId]
cat(sprintf("posts with 1 note: %s | 2-4: %s | 5+: %s | max on one post: %d\n",
            format(sum(per_tweet$N == 1), big.mark = ","),
            format(sum(per_tweet$N %in% 2:4), big.mark = ","),
            format(sum(per_tweet$N >= 5), big.mark = ","),
            max(per_tweet$N)))

# ---- 5. the note TEXT (the only text in this data) --------------------------
cat("\n---- Note 'summary' text ----\n")
notes[, sum_len := nchar(summary)]
cat(sprintf("length chars: median %d | mean %.0f | p95 %d | with URL: %.1f%%\n",
            median(notes$sum_len), mean(notes$sum_len),
            quantile(notes$sum_len, .95),
            100 * mean(grepl("http", notes$summary, fixed = TRUE))))
cat("\nThree examples of 'missing important context' notes (palter-adjacent):\n")
ex <- mis[misleadingMissingImportantContext == 1 & nchar(summary) %between% c(120, 300)][1:3]
for (i in seq_len(nrow(ex)))
  cat(sprintf("  [%s] %s\n", ex$tweetId[i], substr(gsub("\\s+", " ", ex$summary[i]), 1, 200)))

# ---- 6. THE THREE QUESTIONS -------------------------------------------------
cat("\n============================================================\n")
cat("Q1  POST TEXT?   ")
post_text_cols <- grep("tweet.*text|post.*text|full_text", hdr, ignore.case = TRUE, value = TRUE)
cat(if (length(post_text_cols) == 0)
      "NO. Only the post's numeric tweetId is stored; the only free text\n    is the NOTE's own 'summary'. Post text requires rehydration via the X API.\n"
    else paste("YES:", paste(post_text_cols, collapse = ", "), "\n"))

cat("Q2  REPOSTS / CASCADES?   ")
cascade_cols <- grep("retweet|repost|share|cascade|follow", hdr, ignore.case = TRUE, value = TRUE)
cat(if (length(cascade_cols) == 0)
      "NO. No repost counts, no diffusion trees, no follower\n    graph, no engagement of any kind — this file describes NOTES, not spread.\n"
    else paste("YES:", paste(cascade_cols, collapse = ", "), "\n"))

cat("Q3  POST TIMELINE?   PARTIAL — exactly two timestamps are recoverable:\n")
# tweetId is a Twitter snowflake: creation ms = (id >> 22) + 1288834974657
ok <- notes[nchar(tweetId) >= 15]
post_ms <- as.integer64(ok$tweetId) %/% as.integer64(4194304) + as.integer64(1288834974657)
ok[, post_time := as.POSIXct(as.numeric(post_ms) / 1000, origin = "1970-01-01", tz = "UTC")]
delay_h <- as.numeric(difftime(ok$note_time, ok$post_time, units = "hours"))
cat(sprintf("    (a) post creation time — decodable from the snowflake tweetId itself\n"))
cat(sprintf("    (b) note creation time — createdAtMillis\n"))
cat(sprintf("    lag post -> note: median %.1f h | mean %.0f h | 25%%-75%%: %.1f-%.1f h\n",
            median(delay_h, na.rm = TRUE), mean(delay_h, na.rm = TRUE),
            quantile(delay_h, .25, na.rm = TRUE), quantile(delay_h, .75, na.rm = TRUE)))
cat("    NOT recoverable here: when/how the post spread (reposts over time).\n")
cat("    (noteStatusHistory + ratings downloads add the NOTE's own lifecycle only.)\n")

# ---- 7. figures --------------------------------------------------------------
png(file.path(out_dir, "notes_per_month.png"), 1400, 700, res = 130)
mon <- notes[, .N, by = .(m = format(note_time, "%Y-%m"))][order(m)]
par(mar = c(5, 5, 3, 1))
plot(as.Date(paste0(mon$m, "-01")), mon$N, type = "l", lwd = 2,
     xlab = "month", ylab = "notes written", main = "Community Notes volume over time")
dev.off()

png(file.path(out_dir, "misleading_taxonomy.png"), 1400, 700, res = 130)
par(mar = c(5, 14, 3, 1))
bar <- flag_tab[order(n)]
barplot(bar$n / 1000, names.arg = bar$flag, horiz = TRUE, las = 1,
        xlab = "notes (thousands)", main = "Why posts get flagged (misleading notes)")
dev.off()
cat(sprintf("\nFigures -> %s/\n", out_dir))
cat("Done.\n")
