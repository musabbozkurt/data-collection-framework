<?php

declare(strict_types=1);

namespace App;

/** The built-in analyses and the chart types of the Analytics page. The analyses actually offered are worked out per
 * collection by the Python server (command analysismetrics); METRICS is the fallback. */
final class AnalysisOptions
{
    public const METRICS = [
        'tweets_per_profile' => 'Tweets per profile',
        'likes_per_profile' => 'Likes per profile',
        'retweets_per_profile' => 'Retweets per profile',
        'views_per_profile' => 'Views per profile',
        'replies_per_profile' => 'Replies per profile',
        'most_liked' => 'Most liked tweets',
        'hashtags' => 'Top hashtags',
        'top_terms' => 'Most frequent terms',
        'top_pairs' => 'Terms that appear together',
        'word_ngrams' => 'Word n-grams',
        'char_ngrams' => 'Character n-grams',
        'tweet_type' => 'Tweet types (text, media, reply)',
        'media_type' => 'Media types',
        'posts_by_date' => 'Tweets by date',
    ];

    public const CHART_TYPES = [
        'bars' => 'Table with bars', 'columns' => 'Column chart', 'pie' => 'Pie chart'
    ];

    /** The built-in tweet analyses in the format of the server's list, used when the server cannot supply one. */
    public static function fallback(): array
    {
        $list = [];
        foreach (self::METRICS as $key => $label) {
            $list[] = ['key' => $key, 'label' => $label, 'description' => '', 'group' => 'Tweet analyses'];
        }
        return $list;
    }
}
