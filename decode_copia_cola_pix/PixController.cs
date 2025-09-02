using System;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;

namespace PixParserAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PixController : ControllerBase
    {
        [HttpPost("classify")]
        public IActionResult ClassifyPix([FromBody] string pixString)
        {
            try
            {
                var tlv = ParseTlv(pixString);
                var journey = ClassifyJourney(tlv);
                return Ok(journey);
            }
            catch (Exception ex)
            {
                return BadRequest($"Erro no processamento: {ex.Message}");
            }
        }

        private Dictionary<string, object> ParseTlv(string data)
        {
            int index = 0;
            var parsed = new Dictionary<string, object>();

            while (index < data.Length)
            {
                string tag = data.Substring(index, 2);
                int length = int.Parse(data.Substring(index + 2, 2));
                string value = data.Substring(index + 4, length);

                if (IsNestedTemplate(tag))
                {
                    parsed[tag] = ParseTlv(value);
                }
                else
                {
                    parsed[tag] = value;
                }

                index += 4 + length;
            }

            return parsed;
        }

        private bool IsNestedTemplate(string tag)
        {
            int tagInt = int.Parse(tag);
            return (tagInt >= 26 && tagInt <= 51) || (tagInt >= 80 && tagInt <= 99);
        }

        private bool UrlIndicatesRecurrence(string url)
        {
            var keywords = new[] { "/rec/", "recurring", "assinatura", "automatico" };
            foreach (var keyword in keywords)
            {
                if (url.ToLower().Contains(keyword))
                    return true;
            }
            return false;
        }

        private string ClassifyJourney(Dictionary<string, object> tlv)
        {
            string id01 = tlv.ContainsKey("01") ? tlv["01"]?.ToString() : null;
            var id26 = tlv.ContainsKey("26") ? tlv["26"] as Dictionary<string, object> : new Dictionary<string, object>();
            string id54 = tlv.ContainsKey("54") ? tlv["54"]?.ToString() : null;
            var id80 = tlv.ContainsKey("80") ? tlv["80"] as Dictionary<string, object> : new Dictionary<string, object>();

            string gui26 = id26.ContainsKey("00") ? id26["00"]?.ToString() : null;
            string chavePix = id26.ContainsKey("01") ? id26["01"]?.ToString() : null;
            string urlDinamica = id26.ContainsKey("25") ? id26["25"]?.ToString() : null;
            string url80 = id80.ContainsKey("25") ? id80["25"]?.ToString() : null;

            bool hasRecurrenceUrl = !string.IsNullOrEmpty(url80) && UrlIndicatesRecurrence(url80);

            if (hasRecurrenceUrl && gui26 != null && chavePix == null && urlDinamica == null && id54 == null && id01 == null)
                return "journey_2";

            if (hasRecurrenceUrl && urlDinamica != null && id01 != null && id54 == null)
                return "journey_3";

            if (hasRecurrenceUrl && chavePix != null && id54 != null && id01 == null)
                return "journey_4";

            if (!hasRecurrenceUrl && urlDinamica != null && id01 != null)
                return "journey_1";

            return "only_pix";
        }
    }
}
