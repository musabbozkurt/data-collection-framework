<?php

declare(strict_types=1);

namespace App;

/** Renders small SVG charts. Colours come from CSS classes (.chart-c0 ... .chart-c9) so the CSP stays strict. */
final class Chart
{
    private const COLORS = 10;

    /**
     * A table of label/value items shown as "bars" (a bar per row), "columns" (column chart) or "pie".
     *
     * @param array<int, array{label: string, value: int|float}> $items
     */
    public static function view(array $items, string $type, string $unit, string $header = 'Label'): string
    {
        $max = max(1, ...array_map(static fn($row) => (int)$row['value'], $items ?: [['value' => 1]]));
        $html = '';
        if ($type !== 'bars') {
            $html .= '<div class="chart-box">' . ($type === 'pie' ? self::pie($items) : self::columns($items, $unit)) . '</div>';
        }
        $html .= '<table class="table analytics-table"><thead><tr><th>#</th><th>' . self::e($header) . '</th><th>'
            . self::e($unit) . '</th><th></th></tr></thead><tbody>';
        foreach ($items as $i => $row) {
            $html .= '<tr><td>' . ($i + 1) . '</td><td class="analytics-label">' . ($type === 'bars' ? '' : self::swatch($i))
                . self::e((string)$row['label']) . '</td><td>' . number_format((int)$row['value']) . '</td>'
                . '<td class="analytics-bar"><meter min="0" max="' . $max . '" value="' . (int)$row['value'] . '"></meter></td></tr>';
        }
        return $html . '</tbody></table>';
    }

    /**
     * @param list<array{label: string, value: int|float}> $items
     */
    public static function pie(array $items): string
    {
        $total = array_sum(array_map(static fn($i) => max(0.0, (float)$i['value']), $items));
        if ($total <= 0) {
            return '';
        }
        $cx = 150;
        $cy = 150;
        $r = 130;
        $angle = -M_PI / 2;
        $svg = '<svg class="chart chart-pie" viewBox="0 0 300 300" role="img" aria-label="Pie chart" width="300" height="300">';
        foreach (array_values($items) as $i => $item) {
            $share = max(0.0, (float)$item['value']) / $total;
            if ($share <= 0) {
                continue;
            }
            $title = '<title>' . self::e((string)$item['label']) . ': ' . self::e((string)$item['value']) . ' ('
                . number_format($share * 100, 1) . '%)</title>';
            if ($share >= 0.9999) {
                $svg .= '<circle class="chart-c' . ($i % self::COLORS) . '" cx="' . $cx . '" cy="' . $cy
                    . '" r="' . $r . '">' . $title . '</circle>';
                continue;
            }
            $end = $angle + $share * 2 * M_PI;
            $svg .= sprintf(
                '<path class="chart-c%d" d="M %d %d L %.2f %.2f A %d %d 0 %d 1 %.2f %.2f Z">%s</path>',
                $i % self::COLORS, $cx, $cy,
                $cx + $r * cos($angle), $cy + $r * sin($angle), $r, $r, $share > 0.5 ? 1 : 0,
                $cx + $r * cos($end), $cy + $r * sin($end), $title
            );
            $angle = $end;
        }
        return $svg . '</svg>';
    }

    private static function e(string $text): string
    {
        return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }

    /**
     * @param list<array{label: string, value: int|float}> $items
     */
    public static function columns(array $items, string $unit = ''): string
    {
        $count = count($items);
        if ($count === 0) {
            return '';
        }
        $max = max(1.0, ...array_map(static fn($i) => (float)$i['value'], $items));
        $slot = 56;
        $width = max(320, $count * $slot + 60);
        $height = 300;
        $base = 230;
        $svg = '<svg class="chart" viewBox="0 0 ' . $width . ' ' . $height . '" role="img" aria-label="'
            . self::e($unit) . ' column chart" width="' . $width . '" height="' . $height . '">';
        $svg .= '<line class="chart-axis" x1="40" y1="' . $base . '" x2="' . ($width - 10) . '" y2="' . $base . '"/>';
        foreach (array_values($items) as $i => $item) {
            $value = (float)$item['value'];
            $barHeight = (int)round(($value / $max) * 180);
            $x = 50 + $i * $slot;
            $svg .= '<g><title>' . self::e((string)$item['label']) . ': ' . self::e((string)$value) . '</title>'
                . '<rect class="chart-c' . ($i % self::COLORS) . '" x="' . $x . '" y="' . ($base - $barHeight)
                . '" width="' . ($slot - 12) . '" height="' . $barHeight . '"/>'
                . '<text class="chart-value" x="' . ($x + ($slot - 12) / 2) . '" y="' . ($base - $barHeight - 5)
                . '" text-anchor="middle">' . self::e(rtrim(rtrim(number_format($value, 2, '.', ''), '0'), '.')) . '</text>'
                . '<text class="chart-label" transform="translate(' . ($x + ($slot - 12) / 2) . ' ' . ($base + 12)
                . ') rotate(40)">' . self::e(self::short((string)$item['label'])) . '</text></g>';
        }
        return $svg . '</svg>';
    }

    private static function short(string $label, int $length = 14): string
    {
        return mb_strimwidth($label, 0, $length, '…');
    }

    /** Colour swatch matching the slice or bar at this position. */
    public static function swatch(int $index): string
    {
        return '<span class="chart-swatch chart-c' . ($index % self::COLORS) . '"></span>';
    }
}
