#include "CoordUtils.h"
#include <cmath>
namespace SkyHigh::CoordUtils {
static constexpr double R_NM = 3440.065;
double haversineNm(double lat1, double lon1, double lat2, double lon2) {
    auto toRad = [](double d){ return d * 3.14159265358979323846 / 180.0; };
    double dlat = toRad(lat2 - lat1), dlon = toRad(lon2 - lon1);
    double a = std::sin(dlat/2)*std::sin(dlat/2) + std::cos(toRad(lat1))*std::cos(toRad(lat2))*std::sin(dlon/2)*std::sin(dlon/2);
    return 2.0 * R_NM * std::asin(std::sqrt(a));
}
}
