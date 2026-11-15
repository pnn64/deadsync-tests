use deadsync_simfile::song::{ParseSongOptions,parse_song_meta_file};
fn main() {
 let name=std::env::args().nth(1).unwrap();
 for duration in [0.0,95.0] {
  let song=parse_song_meta_file(std::path::Path::new(&name), &ParseSongOptions::new(Vec::new(),Vec::new(),Vec::new()), 0.0, |_|duration).unwrap();
  println!("duration={} last={} note_last={:?} first={} hint={} offset={} charts={}",duration,song.precise_last_second_seconds,song.precise_note_last_second_seconds,song.first_second,song.last_second_hint,song.offset,song.charts.len());
  for c in &song.charts { println!("chart={:?} difficulty={:?} measures={} first={} grade_points={}",c.chart_type,c.difficulty,c.total_measures,c.first_second,c.possible_grade_points); }
 }
}
