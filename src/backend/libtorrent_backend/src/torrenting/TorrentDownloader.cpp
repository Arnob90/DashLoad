#include "TorrentDownloader.hpp"
#include <boost/asio.hpp>
#include <libtorrent/add_torrent_params.hpp>
#include <libtorrent/alert.hpp>
#include <libtorrent/alert_types.hpp>
#include <libtorrent/magnet_uri.hpp>
#include <libtorrent/session.hpp>
#include <string_view>
#include <sys/types.h>
namespace torrentdownloader
{
libtorrent::string_view convert_str_view_to_boost_view(std::string_view given_view)
{
    return {given_view.data(), given_view.size()};
}
void TorrentDownloader::start_download(std::string_view magnet_link, std::string_view filepath_to_save_in)
{
    lt::add_torrent_params params = lt::parse_magnet_uri(convert_str_view_to_boost_view(magnet_link));
    params.save_path = filepath_to_save_in;
    main_session.async_add_torrent(params);
    alert_handler.connect<lt::add_torrent_alert>(lt::add_torrent_alert::type(), &TorrentDownloader::handle_torrent_added_callback);
}
lt::session TorrentDownloader::main_session = lt::session();
void TorrentDownloader::pause_download(std::string_view id_to_pause)
{
    id_to_downloads.at(id_to_pause.data()).pause();
}
} // namespace torrentdownloader
