use Image::ExifTool qw(:Public);
my @keys=qw(DateTimeOriginal|CreateDate|GPSDateTime FNumber ExposureMode ExposureTime ImageSize CircleOfConfusion FOV FocalLength ISO Sharpness WhiteBalance FacesDetected Make Model Flash Copyright Software);
my $info = ImageInfo('image.jpg');
my $info2 = ImageInfo('/home/john/Desktop/IMGP1382.JPG');

foreach (keys %$info) {
    print "$_ => $$info{$_} :: $$info2{$_}\n";
}
